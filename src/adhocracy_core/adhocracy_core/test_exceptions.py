"""Test creation of Exceptions."""


def test_configuration_error_create():
    from .exceptions import ConfigurationError
    inst = ConfigurationError()
    assert inst


def test_configuration_error_to_str_empty():
    from .exceptions import ConfigurationError
    inst = ConfigurationError()
    assert str(inst) == ''
    assert repr(inst) == ''


def test_configuration_error_to_str_with_details():
    from .exceptions import ConfigurationError
    inst = ConfigurationError('details')
    assert str(inst) == 'details'
    assert repr(inst) == 'details'


def test_auto_update_no_fork_allowed_error_create():
    from .exceptions import AutoUpdateNoForkAllowedError
    resource = object()
    event = object()
    inst = AutoUpdateNoForkAllowedError(resource, event)
    assert inst.resource is resource
    assert inst.event is event
