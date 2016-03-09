"""
Badge assignment workflow.

This workflow can be defined on badge resources to specify who are
allowed to assign them.

"""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_core.workflows:badge_assignment.yaml',
                        'badge_assignment')
