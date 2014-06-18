import unittest


class ClientUnitTests(unittest.TestCase):

    def test_websocket_client_installed(self):
        """Test that websocket-client is installed."""
        import websocket
