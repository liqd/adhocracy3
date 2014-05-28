import unittest

from pyramid import testing
import colander
import pytest

from adhocracy.websockets.schemas import ClientRequestSchema
from adhocracy.websockets.schemas import StatusConfirmation


class ClientRequestSchemaUnitTests(unittest.TestCase):

    """Test ClientRequestSchema deserialization."""

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()
        self.context['child'] = self.child

    def _make_one(self):
        schema = ClientRequestSchema()
        return schema.bind(context=self.context)

    def test_deserialize_subscribe(self):
        inst = self._make_one()
        result = inst.deserialize(
            {'action': 'subscribe', 'resource': '/child'})
        assert result == {'action': 'subscribe', 'resource': self.child}

    def test_deserialize_unsubscribe(self):
        inst = self._make_one()
        result = inst.deserialize(
            {'action': 'unsubscribe', 'resource': '/child'})
        assert result == {'action': 'unsubscribe', 'resource': self.child}

    def test_deserialize_invalid_action(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 'blah', 'resource': '/child'})

    def test_deserialize_invalid_resource(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize(
                {'action': 'subscribe', 'resource': '/wrong_child'})

    def test_deserialize_no_action(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'resource': '/child'})

    def test_deserialize_no_resource(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 'subscribe'})

    def test_deserialize_empty_dict(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_wrong_inner_type(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 7, 'resource': '/child'})

    def test_deserialize_wrong_outer_type(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize(['subscribe'])

class StatusConfirmationUnitTests(unittest.TestCase):

    """Test StatusConfirmation serialization."""

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()
        self.context['child'] = self.child

    def _make_one(self):
        schema = StatusConfirmation()
        return schema.bind(context=self.context)

    def test_serialize_ok(self):
        inst = self._make_one()
        result = inst.serialize(
            {'status': 'ok', 'action': 'subscribe', 'resource': self.child})
        assert result == {'status': 'ok',
                          'action': 'subscribe',
                          'resource': '/child'}

    def test_serialize_duplicate(self):
        inst = self._make_one()
        result = inst.serialize(
            {'status': 'duplicate',
             'action': 'unsubscribe',
             'resource': self.child})
        assert result == {'status': 'duplicate',
                          'action': 'unsubscribe',
                          'resource': '/child'}

    def test_serialize_default_status(self):
        inst = self._make_one()
        result = inst.serialize({'action': 'subscribe',
                                 'resource': self.child})
        assert result == {'status': 'ok',
                          'action': 'subscribe',
                          'resource': '/child'}
