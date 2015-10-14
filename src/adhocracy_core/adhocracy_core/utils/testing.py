"""Functionalities to ease the testing of Adhocracy."""

import transaction

from pyramid.router import Router
from webtest import TestResponse

from adhocracy_core.scripts import import_resources
from adhocracy_core.utils import get_root


def add_resources(app: Router, filename: str):
    """Add resources from a JSON file to the app."""
    root = get_root(app)
    import_resources(root, app.registry, filename)
    transaction.commit()


def do_transition_to(app_user, path, state) -> TestResponse:
    """Transition to a new workflow state by sending a PUT request."""
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:
                     {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp
