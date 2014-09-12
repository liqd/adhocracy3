from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy.registry')
    config.include('adhocracy.events')
    config.include('adhocracy.sheets.metadata')
    config.include('adhocracy.resources.service')


@mark.usefixtures('integration')
def test_includeme_registry_register_factories(registry):
    from adhocracy.resources.service import IBasicService
    content_types = registry.content.factory_types
    assert IBasicService.__identifier__ in content_types


@mark.usefixtures('integration')
def test_includeme_registry_create_content(registry, pool):
    from adhocracy.resources.service import IBasicService
    service = registry.content.create(IBasicService.__identifier__, parent=pool)
    assert service.__is_service__
