from pytest import mark
from pytest import raises
from pytest import fixture
from pyramid import testing


def test_changelog_create():
    from . import Changelog
    from . import changelog_meta
    inst = Changelog()
    assert inst['/path/'] == changelog_meta


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')


@mark.usefixtures('integration')
def test_includeme_add_changelog(registry):
    from . import Changelog
    assert isinstance(registry.changelog, Changelog)


@mark.usefixtures('integration')
def test_clear_changelog_after_commit_hook(context, registry, changelog):
    from . import clear_changelog_after_commit_hook
    changelog['/'] = changelog['/']._replace(resource=context)
    registry.changelog = changelog
    clear_changelog_after_commit_hook(True, registry)
    assert changelog['/'].resource is None


def test_clear_modification_date_after_commit_hook(registry):
    from adhocracy_core.utils import get_modification_date
    from . import clear_modification_date_after_commit_hook
    date_before = get_modification_date(registry)
    clear_modification_date_after_commit_hook(True, registry)
    date_after = get_modification_date(registry)
    assert date_before is not date_after
