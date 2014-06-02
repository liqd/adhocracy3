import unittest

from pyramid import testing
import colander
import pytest

from adhocracy.websockets.schemas import *


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


class NotificationUnitTests(unittest.TestCase):

    """Test serialization of Notification and its subclasses."""

    def setUp(self):
        self.context = testing.DummyResource()
        self.parent = testing.DummyResource()
        self.context['parent'] = self.parent

    def _bind(self, schema: Notification) -> Notification:
        return schema.bind(context=self.context)

    def test_serialize_notification(self):
        schema = Notification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'modified', 'resource': self.parent})
        assert result == {'event': 'modified', 'resource': '/parent'}

    def test_serialize_child_notification(self):
        self.child = testing.DummyResource('child', self.parent)
        schema = ChildNotification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'removed_child',
                                 'resource': self.parent,
                                 'child': self.child})
        assert result == {'event': 'removed_child',
                          'resource': '/parent',
                          'child': '/parent/child'}

    def test_serialize_version_notification(self):
        self.version = testing.DummyResource('version', self.parent)
        schema = VersionNotification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'removed_child',
                                 'resource': self.parent,
                                 'version': self.version})
        assert result == {'event': 'removed_child',
                          'resource': '/parent',
                          'version': '/parent/version'}

