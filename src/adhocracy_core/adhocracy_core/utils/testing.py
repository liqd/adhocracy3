"""Functionalities to ease the testing of Adhocracy."""

import transaction

from pyramid.router import Router
from pyramid.threadlocal import manager
from webtest import TestResponse

from adhocracy_core.scripts import import_resources
from adhocracy_core.utils import get_root


def add_resources(app_router: Router, filename: str):
    """Add resources from a JSON file to the app."""
    manager.push({'registry': app_router.registry})
    try:
        root = get_root(app_router)
        import_resources(root, app_router.registry, filename)
        transaction.commit()
    finally:
        manager.pop()


def do_transition_to(app_user, path, state) -> TestResponse:
    """Transition to a new workflow state by sending a PUT request."""
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:
                     {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp
