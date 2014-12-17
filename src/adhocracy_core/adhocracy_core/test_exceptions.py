"""Test creation of Exceptions."""


def test_auto_update_no_fork_allowed_error_create():
    from .exceptions import AutoUpdateNoForkAllowedError
    resource = object()
    event = object()
    inst = AutoUpdateNoForkAllowedError(resource, event)
    assert inst.resource is resource
    assert inst.event is event
