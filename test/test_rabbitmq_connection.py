import os
import pytest
from kombu import Connection
from kombu.exceptions import OperationalError

# You can set default values for connection parameters here, or use environment variables.
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@localhost:5672//")

@pytest.mark.integration
def test_rabbitmq_connection():
    """
    Integration test for RabbitMQ connection using Kombu.
    Attempts to establish a connection and checks that it is successful.
    """
    try:
        with Connection(RABBITMQ_URL) as conn:
            conn.connect()
            assert conn.connected, "Failed to connect to RabbitMQ"
            print("Connection successful!")
    except OperationalError as e:
        pytest.fail(f"Connection failed: {e}")
