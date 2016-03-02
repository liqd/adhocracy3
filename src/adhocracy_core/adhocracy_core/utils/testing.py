"""Functionalities to ease the testing of Adhocracy."""

import transaction

from pyramid.router import Router
from pyramid.scripting import get_root
from webtest import TestResponse

from adhocracy_core.scripts import import_resources
from adhocracy_core.scripts import import_local_roles


def add_resources(app_router: Router, filename: str):
    """Add resources from a JSON file to the app."""
    _run_import_function(import_resources, app_router, filename)


def add_local_roles(app_router: Router, filename: str):
    """Add local roles from a JSON file to resources."""
    _run_import_function(import_local_roles, app_router, filename)


def _run_import_function(func: callable, app_router: Router, filename: str):
    root, closer = get_root(app_router)
    try:
        func(root, app_router.registry, filename)
        transaction.commit()
    finally:
        closer()


def do_transition_to(app_user, path, state) -> TestResponse:
    """Transition to a new workflow state by sending a PUT request."""
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:
                     {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp
