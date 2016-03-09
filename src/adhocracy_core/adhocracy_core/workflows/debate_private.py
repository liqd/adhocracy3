"""Private debate workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_core.workflows:debate_private.yaml',
                        'debate_private')
