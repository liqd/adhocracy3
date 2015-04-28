"""Common fixtures for adhocracy_mercator."""
from pytest import fixture


@fixture(scope='class')
def app(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from pyramid.config import Configurator
    from adhocracy_core.testing import add_create_test_users_subscriber
    import adhocracy_mercator
    import adhocracy_mercator.resources.mercator
    import adhocracy_core.resources.sample_paragraph
    import adhocracy_core.resources.sample_section
    import adhocracy_core.resources.sample_proposal
    configurator = Configurator(settings=app_settings,
                                root_factory=adhocracy_mercator.root_factory)
    configurator.include(adhocracy_mercator)
    configurator.include(adhocracy_core.resources.sample_paragraph)
    configurator.include(adhocracy_core.resources.sample_proposal)
    configurator.include(adhocracy_core.resources.sample_section)
    configurator.include(adhocracy_core.resources.comment)
    configurator.include(adhocracy_core.resources.rate)
    configurator.include(adhocracy_mercator.resources.mercator)
    configurator.commit()
    add_create_test_users_subscriber(configurator)
    app = configurator.make_wsgi_app()
    return app
