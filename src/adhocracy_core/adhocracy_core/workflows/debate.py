"""Debate workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_core.workflows:debate.yaml', 'debate')
