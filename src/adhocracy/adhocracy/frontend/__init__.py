"""View configurations."""


def includeme(config):
    """Run pyramid config."""
    config.add_static_view('frontend_static', 'adhocracy.frontend:static')
