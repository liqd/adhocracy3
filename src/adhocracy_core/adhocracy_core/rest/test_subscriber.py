from pyramid import testing
from pytest import fixture
from pytest import mark


def test_add_cors_headers(context):
    from .subscriber import add_cors_headers
    headers = {}
    response = testing.DummyResource(headers=headers)
    event = testing.DummyResource(response=response)

    add_cors_headers(event)

    assert headers == \
        {'Access-Control-Allow-Origin': '*',
         'Access-Control-Allow-Headers':
         'Origin, Content-Type, Accept, X-User-Path, X-User-Token',
         'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS'}


@fixture()
def integration(config):
    config.include('adhocracy_core.rest.subscriber')


@mark.usefixtures('integration')
class TestIntegrationIncludeme:

    def test_register_subscriber(self, registry):
        from .subscriber import add_cors_headers
        handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
        assert add_cors_headers.__name__ in handlers

