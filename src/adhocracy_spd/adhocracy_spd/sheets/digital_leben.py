"""Sheets for digital leven process."""
from zope.deprecation import deprecated

from adhocracy_core.sheets import workflow


class IWorkflowAssignment(workflow.IWorkflowAssignment):
    """Marker interface for the digital leben workflow assignment sheet."""


deprecated('IWorkflowAssignment',
           'Backward compatible code use process IWorkflowAssignment instead')
