"""Resource type configuration."""


def includeme(config):
    """Include resource types."""
    config.include('.subscriber')
    config.include('.idea_collection')
    config.include('.collaborative_text')
