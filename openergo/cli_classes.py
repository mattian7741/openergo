# cli_classes.py
import os
import sys
import logging
from kombu import Connection, Exchange, Queue
import json
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)


class OpenergoCLI(ABC):
    def __init__(self, config_file=None):
        self.config = self.load_config(config_file)

    def load_config(self, config_file):
        """Utility method to load JSON configuration from a file."""
        config_data = {}
        if config_file:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        return config_data

    @abstractmethod
    def handle(self, *args, **kwargs):
        """Handle the protocol with specific logic."""
        pass

class StdioCLI(OpenergoCLI):
    def handle(self):
        logging.info("Handling stdio protocol")
        logging.info(f"Config: {self.config}")
        
        # Check if there is any piped input from stdin
        if not sys.stdin.isatty():  # This checks if stdin is connected to a pipe or file
            piped_data = sys.stdin.read()  # Read all piped data from stdin
            logging.info("Piped input data:")
            logging.info(piped_data)  # Output the piped data to the terminal
        else:
            logging.info("No piped input data detected.")


class AmqpCLI(OpenergoCLI):
    def __init__(self, config_file):
        super().__init__(config_file)
        
        # Extract configuration details
        self.routing_keys = self.config.get("output_keys")  # Routing keys from config
       
        # Prepare exchange, queue name, and input keys
        self.exchange_name = self.config.get("namespace")  # Exchange from config `namespace`
        self.queue_name = f"q-{self.config.get('name')}"   # Queue name derived from `name` in config
        self.bindings = [self.prepare_key(key) for key in self.config.get("input_keys", [])]  # Bindings from input keys
        
        # Initialize connection directly with the connection URL
        self.connection = Connection("amqp://user:password@localhost:5672//")  # Replace with actual credentials
        
        # Prefetch count for consuming, set from environment variable BATCH_SIZE or default to 1
        self.prefetch_count = int(os.getenv("BATCH_SIZE", 6))
        
        # Warn if BATCH_SIZE environment variable is not set
        if "BATCH_SIZE" not in os.environ:
            logging.warning("Environment variable BATCH_SIZE is not set. Defaulting prefetch count to 1.")

        # Lazy-initialized members
        self._producer = None
        self._consumer = None

        # Initialize exchange and queue setup at instantiation
        self.setup_connection()

    @property
    def producer(self):
        """Getter for producer with lazy initialization."""
        if self._producer is None:
            self._producer = self.connection.Producer(channel=self.connection.channel(), serializer="json")
        return self._producer

    @property
    def consumer(self):
        """Getter for consumer with lazy initialization."""
        if self._consumer is None:
            # Set up consumer with prefetch settings and use the process_message callback
            consume_channel = self.connection.channel()
            consume_channel.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)
            self._consumer = self.connection.Consumer(self.queue, channel=consume_channel, callbacks=[self.process_message], accept=["json"])
        return self._consumer

    def setup_connection(self):
        """Initialize exchange and queue for publishing and consuming."""
        with self.connection.channel() as channel:
            # Lazily initialize the exchange and queue
            self.exchange = self.initialize_exchange(channel)
            self.queue = self.initialize_queue(channel)

    def handle(self):
        logging.info("Handling amqp protocol")
        logging.info(f"Config: {self.config}")
        logging.info(f"Transformed bindings: {self.bindings}")

        # Use the lazily initialized consumer for message consumption
        with self.consumer:
            try:
                self.connection.drain_events(timeout=5)  # Adjust timeout as needed
            except Exception as e:
                logging.error(f"Error while consuming message: {e}")

    def initialize_exchange(self, channel):
        """Lazily initialize the exchange."""
        exchange = Exchange(self.exchange_name, type="topic", durable=True)
        exchange(channel).declare()  # This will only create if it doesn't exist
        return exchange

    def initialize_queue(self, channel):
        """Lazily initialize the queue and bind prepared input keys."""
        queue = Queue(self.queue_name, self.exchange, durable=True)
        bound_queue = queue(channel)  # Bind queue to the channel
        
        # Bind each prepared input key (binding) to the queue
        for binding in self.bindings:
            bound_queue.bind_to(self.exchange, routing_key=binding)

        return bound_queue

    def prepare_key(self, key):
        """Prepare and transform the input key by sorting and adding wildcards."""
        # Sort the segments within the key
        sorted_segments = sorted(key.split('.'))
        # Insert wildcards between each segment and at the edges
        transformed_key = '#.' + '.#.'.join(sorted_segments) + '.#'
        return transformed_key

    def process_message(self, body, message):
        """Process a consumed message, modify it, and republish to the exchange."""
        logging.info(f"Received message: {body}")

        # Modify payload keys by appending "_"
        modified_payload = {f"{key}_": value for key, value in body.items()}
        logging.info(f"Modified payload: {modified_payload}")

        # Publish the modified payload to the exchange using the dedicated producer
        self.producer.publish(
            modified_payload,
            exchange=self.exchange,
            routing_key=self.routing_keys[0],  # Use the first routing key from the config
            declare=[self.exchange],
            retry=True,
            headers={
                "content_type": "application/json",
                "content_encoding": "utf-8"
            }
        )
        logging.info(f"Published modified message to exchange '{self.exchange_name}' with routing key '{self.routing_keys[0]}'.")

        # Acknowledge the original message to remove it from the queue
        message.ack()


class EventloopCLI(OpenergoCLI):
    def handle(self):
        logging.info("Handling eventloop protocol")
        logging.info(f"Config: {self.config}")

class GraphCLI(OpenergoCLI):
    def __init__(self, config_file=None, routing_keys=None):
        super().__init__(config_file)
        self.routing_keys = routing_keys or []

    def handle(self):
        logging.info("Handling graph protocol")
        logging.info(f"Config: {self.config}")
        logging.info(f"Routing keys: {self.routing_keys}")
