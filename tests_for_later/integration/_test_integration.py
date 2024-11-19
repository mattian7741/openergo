import unittest
from openergo.complete import AmqpInputConnector, AmqpOutputConnector

class TestAmqpConnectorIntegration(unittest.TestCase):
    def test_real_message_publish_and_receive(self):
        publisher = AmqpOutputConnector({'exchange': 'test', 'routing_key': 'route'})
        consumer = AmqpInputConnector({'queue': 'test'})
        test_message = "Integration Test Message"
        publisher.publish_message(test_message)
        # Assert that the consumer receives the message, possibly with timeouts and retries

if __name__ == '__main__':
    unittest.main()
