from pytest import mark
from pytest import fixture
from pyramid import testing


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')


@fixture()
def request_(registry):
    request = testing.DummyResource(registry=registry)
    return request


@mark.usefixtures('integration')
def test_add_changelog(registry):
    assert hasattr(registry, 'changelog')


@mark.usefixtures('integration')
def test_clear_changelog(context, registry, request_, changelog):
    from . import clear_changelog_callback
    changelog['/'] = changelog['/']._replace(resource=context)
    registry.changelog = changelog
    clear_changelog_callback(request_)
    assert changelog['/'].resource is None


def test_clear_modification_date(registry, request_):
    from adhocracy_core.utils import get_modification_date
    from . import clear_modification_date_callback
    date_before = get_modification_date(registry)
    clear_modification_date_callback(request_)
    date_after = get_modification_date(registry)
    assert date_before is not date_after
