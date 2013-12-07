"""py.test test fixtures: http://pytest.org/latest/fixture.html"""
from pytest import fixture


def settings_functional():
    """Return minimal pyramid config for functional tests."""
    settings = settings_integration()
    settings.update({"pyramid.includes": ["pyramid_zodbconn", "pyramid_tm"],
                     "substanced.initial_login": "admin",
                     "substanced.initial_password": "admin",
                     "substanced.initial_email": "admin@example.com",
                     "substanced.secret": "secret",
                     "substanced.autosync_catalogs": "true",
                     "substanced.statsd.enabled": "false ",
                     "substanced.autoevolve": "true",
                     })
    return settings


def settings_integration():
    """Return minimal pyramid config for integration tests."""
    return {"zodbconn.uri": "memory://",
            }


@fixture
def config(request):
    """ Return a dummy pyramid config object and tear down after testing. """
    import pyramid.testing
    dummy_request = pyramid.testing.DummyRequest()
    config_ = pyramid.testing.setUp(settings=settings_integration(),
                                    request=dummy_request)
    request.addfinalizer(pyramid.testing.tearDown)
    return config_
