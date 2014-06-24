import unittest


class WebSocketErrorUnitTests(unittest.TestCase):

    """Test the WebSocketError class."""

    def test_str(self):
        from adhocracy.websockets import WebSocketError
        err = WebSocketError('malformed_message', 'message is binary')
        assert str(err) == 'malformed_message: message is binary'
