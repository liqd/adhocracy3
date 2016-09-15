import unittest

from pyramid import testing
from adhocracy_core.interfaces import API_ROUTE_NAME
from adhocracy_core.testing import rest_url
import colander
import pytest


def _setup_config_and_request(root):
    config = testing.setUp()
    config.add_route(API_ROUTE_NAME, '/api*traverse')
    request = testing.DummyRequest()
    request.root = root
    request.registry = config.registry
    request.application_url = 'http://localhost'
    return request


class ClientRequestSchemaUnitTests(unittest.TestCase):

    """Test ClientRequestSchema deserialization."""

    def setUp(self):
        child = testing.DummyResource()
        self.child = child
        root = testing.DummyResource()
        root['child'] = child
        self.context = root
        self.request = _setup_config_and_request(root)
        self.rest_url = rest_url()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self):
        from adhocracy_core.websockets.schemas import ClientRequestSchema
        schema = ClientRequestSchema()
        return schema.bind(request=self.request, context=self.context)

    def test_deserialize_subscribe(self):
        inst = self._make_one()
        result = inst.deserialize(
            {'action': 'subscribe', 'resource': self.rest_url + '/child/'})
        assert result == {'action': 'subscribe', 'resource': self.child}

    def test_deserialize_unsubscribe(self):
        inst = self._make_one()
        result = inst.deserialize(
            {'action': 'unsubscribe', 'resource': self.rest_url + '/child/'})
        assert result == {'action': 'unsubscribe', 'resource': self.child}

    def test_deserialize_invalid_action(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 'blah', 'resource': self.rest_url + '/child'})

    def test_deserialize_invalid_resource(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize(
                {'action': 'subscribe', 'resource': self.rest_url + '/wrong_child'})

    def test_deserialize_no_action(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'resource': self.rest_url + '/child'})

    def test_deserialize_no_resource(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 'subscribe'})

    def test_deserialize_empty_dict(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_wrong_field(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'event': 'created', 'resource': self.rest_url + '/child'})

    def test_deserialize_wrong_inner_type(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'action': 7, 'resource': self.rest_url + '/child'})

    def test_deserialize_wrong_outer_type(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize(['subscribe'])


class StatusConfirmationUnitTests(unittest.TestCase):

    """Test StatusConfirmation serialization."""

    def setUp(self):
        child = testing.DummyResource()
        self.child = child
        root = testing.DummyResource()
        root['child'] = child
        self.request = _setup_config_and_request(root)
        self.rest_url = rest_url()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self):
        from adhocracy_core.websockets.schemas import StatusConfirmation
        schema = StatusConfirmation()
        return schema.bind(request=self.request)

    def test_serialize_ok(self):
        inst = self._make_one()
        result = inst.serialize(
            {'status': 'ok', 'action': 'subscribe', 'resource': self.child})
        assert result == {'status': 'ok',
                          'action': 'subscribe',
                          'resource': self.rest_url + '/child/'}

    def test_serialize_redundant(self):
        inst = self._make_one()
        result = inst.serialize(
            {'status': 'redundant',
             'action': 'unsubscribe',
             'resource': self.child})
        assert result == {'status': 'redundant',
                          'action': 'unsubscribe',
                          'resource': self.rest_url + '/child/'}

    def test_serialize_default_status(self):
        inst = self._make_one()
        result = inst.serialize({'action': 'subscribe',
                                 'resource': self.child})
        assert result == {'status': 'ok',
                          'action': 'subscribe',
                          'resource': self.rest_url + '/child/'}


class ServerNotificationUnitTests(unittest.TestCase):

    """Test serialization of ServerNotification and its subclasses."""

    def setUp(self):
        parent = testing.DummyResource()
        self.parent = parent
        context = testing.DummyResource()
        context['parent'] = parent
        self.context = context

    def _bind(self, schema: colander.SchemaNode) -> colander.SchemaNode:
        return schema.bind(context=self.context)

    def test_serialize_notification(self):
        from adhocracy_core.websockets.schemas import ServerNotification
        schema = ServerNotification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'modified', 'resource': self.parent})
        assert result == {'event': 'modified', 'resource': '/parent'}

    def test_deserialize_notification(self):
        from adhocracy_core.websockets.schemas import ServerNotification
        schema = ServerNotification()
        inst = self._bind(schema)
        result = inst.deserialize(
            {'event': 'created', 'resource': '/parent'})
        assert result == {'event': 'created', 'resource': self.parent}


class NotificationUnitTests(unittest.TestCase):

    """Test serialization of Notification and its subclasses."""

    def setUp(self):
        parent = testing.DummyResource()
        self.parent = parent
        root = testing.DummyResource()
        root['parent'] = parent
        self.context = root
        self.request = _setup_config_and_request(root)
        self.rest_url = rest_url()

    def tearDown(self):
        testing.tearDown()

    def _bind(self, schema: colander.SchemaNode) -> colander.SchemaNode:
        return schema.bind(request=self.request, context=self.context)

    def test_serialize_notification(self):
        from adhocracy_core.websockets.schemas import Notification
        schema = Notification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'modified', 'resource': self.parent})
        assert result == {'event': 'modified', 'resource': self.rest_url + '/parent/'}

    def test_deserialize_notification(self):
        from adhocracy_core.websockets.schemas import Notification
        schema = Notification()
        inst = self._bind(schema)
        result = inst.deserialize(
            {'event': 'created', 'resource': self.rest_url + '/parent/'})
        assert result == {'event': 'created', 'resource': self.parent}

    def test_serialize_child_notification(self):
        from adhocracy_core.websockets.schemas import ChildNotification
        self.child = testing.DummyResource('child', self.parent)
        schema = ChildNotification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'removed_child',
                                 'resource': self.parent,
                                 'child': self.child})
        assert result == {'event': 'removed_child',
                          'resource': self.rest_url + '/parent/',
                          'child': self.rest_url + '/parent/child/'}

    def test_serialize_version_notification(self):
        from adhocracy_core.websockets.schemas import VersionNotification
        self.version = testing.DummyResource('version', self.parent)
        schema = VersionNotification()
        inst = self._bind(schema)
        result = inst.serialize({'event': 'removed_child',
                                 'resource': self.parent,
                                 'version': self.version})
        assert result == {'event': 'removed_child',
                          'resource': self.rest_url + '/parent/',
                          'version': self.rest_url + '/parent/version/'}
