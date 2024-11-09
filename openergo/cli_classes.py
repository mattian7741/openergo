# cli_classes.py
import os
import sys
import json
import logging
import subprocess
import importlib
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from io import StringIO
from kombu import Connection, Exchange, Queue
from .KeyStore import KeyStoreBase  # Import the key store interface
import jsonpath_ng  # This library allows for the extraction of values using jsonpath

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Define the Operation abstract base class
class Operation(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass

class PythonOperation(Operation):
    def __init__(self, procedure_path, bindings):
        module_str, function_str = procedure_path.rsplit('.', 1)
        self.module = importlib.import_module(module_str)
        self.function = getattr(self.module, function_str)
        self.bindings = bindings

    def execute(self, **kwargs):
        # Combining default bindings with runtime passed arguments
        final_args = {**self.bindings, **kwargs}
        with StringIO() as output:
            with redirect_stdout(output):
                result = self.function(**final_args)
            output_value = output.getvalue()
        return result if result is not None else output_value.strip()

class BashOperation(Operation):
    def __init__(self, command):
        self.command = command

    def execute(self):
        # Execute the Bash command and return its output
        try:
            result = subprocess.check_output(self.command, shell=True, text=True)
            return json.loads(result)  # Attempt to parse as JSON
        except subprocess.CalledProcessError as e:
            logging.error(f"Bash command failed: {e}")
            return None
        except json.JSONDecodeError:
            return result.strip()  # Return raw output if JSON parsing fails


class StreamToLogger(StringIO):
    def __init__(self, logger, level):
        super().__init__()
        self.logger = logger
        self.level = level

    def write(self, message):
        message = message.strip()
        if message:
            self.logger.log(self.level, message)

    def flush(self):
        pass  # For compatibility with StringIO


class OpenergoCLI(ABC):
    def __init__(self, config_file=None, keystore: KeyStoreBase = None):
        self.config = self.load_config(config_file)
        self.operation = self.load_operation()
        self.keystore = keystore

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return json.load(file)

    def load_operation(self):
        shell_config = self.config.get("shell", {})
        language = shell_config.get("language")
        procedure = shell_config.get("procedure")
        bindings = self.config.get("input", {}).get("bindings", {})

        if language == "python":
            return PythonOperation(procedure, bindings)
        elif language == "bash":
            return BashOperation(procedure)
        else:
            raise ValueError(f"Unsupported operation language: {language}")

    def prepare_arguments_from_message(self, message):
        args = {}
        for arg_name, path in self.config.get("input", {}).get("bindings", {}).items():
            value = self.extract_value_from_message(message, self.parse_binding_path(path))
            if value is not None:
                args[arg_name] = value
        return args

    def parse_binding_path(self, path):
        return path.strip('{}')

    def extract_value_from_message(self, message, path):
        try:
            for part in path.split('.'):
                message = message[part]
            return message
        except (KeyError, TypeError):
            logging.error(f"Path '{path}' not found in message")
            return None

    @abstractmethod
    def handle(self):
        pass


class StdioCLI(OpenergoCLI):
    logger = logging.getLogger("StdioCLI")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def handle(self):
        self.logger.info("Handling stdio protocol")
        self.logger.info(f"Config: {self.config}")

        # Read JSON input from STDIN
        try:
            json_input = json.load(sys.stdin)
            self.logger.info(f"Received input: {json_input}")
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from STDIN")
            return

        # Prepare arguments from JSON input using the binding configuration
        args = self.prepare_arguments_from_message(json_input)

        # Execute the operation with the prepared arguments
        if self.operation:
            try:
                result = self.operation.execute(**args)
                print(json.dumps(result))
            except Exception as e:
                self.logger.error(f"Error while executing operation: {e}")
        else:
            self.logger.error("No valid operation to execute.")

class AmqpCLI(OpenergoCLI):
    def __init__(self, config_file, keystore: KeyStoreBase):
        super().__init__(config_file, keystore)
        self.routing_keys = self.config.get("output", {}).get("keys", [])
        self.exchange_name = self.config.get("namespace")
        self.queue_name = f"q-{self.config.get('name')}"
        self.bindings = [self.prepare_key(key) for key in self.config.get("input", {}).get("keys", [])]
        # Use keystore to retrieve the RabbitMQ URL
        self.connection_url = self.keystore.retrieve_key("RABBITMQ_URL") if self.keystore else None
        self.prefetch_count = int(os.getenv("BATCH_SIZE", 1))
        self.setup_connection()

    def handle(self):
        logging.info("Handling amqp protocol")
        logging.info(f"Config: {self.config}")

        with self.consumer:
            try:
                self.connection.drain_events(timeout=5)
            except Exception as e:
                logging.error(f"Error while consuming message: {e}")

    @property
    def producer(self):
        if not hasattr(self, '_producer'):
            self._producer = self.connection.Producer(channel=self.connection.channel(), serializer="json")
        return self._producer

    @property
    def consumer(self):
        if not hasattr(self, '_consumer'):
            consume_channel = self.connection.channel()
            consume_channel.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)
            self._consumer = self.connection.Consumer(self.queue, channel=consume_channel,
                                                      callbacks=[self.process_message], accept=["json"])
        return self._consumer

    def setup_connection(self):
        # Establish a connection using the retrieved URL
        if not self.connection_url:
            raise ValueError("RABBITMQ_URL is not available in the key store.")
        self.connection = Connection(self.connection_url)
        with self.connection.channel() as channel:
            self.exchange = Exchange(self.exchange_name, type="topic", durable=True)(channel)
            self.queue = Queue(self.queue_name, self.exchange, durable=True)(channel)
            self.queue.declare()
            for binding in self.bindings:
                self.queue.bind_to(self.exchange, routing_key=binding)

    def prepare_key(self, key):
        sorted_segments = sorted(key.split('.'))
        return '#.' + '.#.'.join(sorted_segments) + '.#'

    def process_message(self, body, message):
        logging.info(f"Received message: {body}")
        if not self.operation:
            logging.error("No valid operation to execute.")
            message.ack()
            return

        # Prepare arguments from message using the binding configuration
        args = self.prepare_arguments_from_message(body)

        # Execute the operation with the prepared arguments
        modified_payload = self.operation.execute(**args)
        if modified_payload is None:
            logging.error("Operation failed; skipping message processing.")
            message.ack()
            return

        # Publish results and acknowledge message
        self.publish_message(modified_payload)
        message.ack()

    def publish_message(self, payload):
        self.producer.publish(
            payload,
            exchange=self.exchange,
            routing_key=self.routing_keys[0],
            declare=[self.exchange],
            retry=True,
            headers={
                "content_type": "application/json",
                "content_encoding": "utf-8"
            }
        )
        logging.info(f"Published message {payload} with routing key '{self.routing_keys[0]}'")


class EventloopCLI(OpenergoCLI):
    def handle(self):
        logging.info("Handling eventloop protocol")
        logging.info(f"Config: {self.config}")
        if self.operation:
            result = self.operation.execute()
            logging.info(f"Eventloop operation result: {result}")


class GraphCLI(OpenergoCLI):
    def __init__(self, config_file=None, routing_keys=None, keystore: KeyStoreBase = None):
        super().__init__(config_file, keystore)
        self.routing_keys = routing_keys or []

    def handle(self):
        logging.info("Handling graph protocol")
        logging.info(f"Config: {self.config}")
        logging.info(f"Routing keys: {self.routing_keys}")
        if self.operation:
            result = self.operation.execute()
            logging.info(f"Graph operation result: {result}")
