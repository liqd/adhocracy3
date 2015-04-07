from unittest.mock import Mock

from pytest import mark
from pytest import raises
from pytest import fixture
from pyramid import testing


@fixture
def event(changelog, context):
    registry = testing.DummyResource()
    registry.changelog = changelog
    event = testing.DummyResource(object=context, registry=registry)
    return event


def test_add_changelog_created(event, changelog):
    from .subscriber import add_changelog_created
    add_changelog_created(event)
    assert changelog['/'].created is True


def test_add_changelog_created_password_reset(event, changelog):
    from adhocracy_core.resources.principal import IPasswordReset
    from .subscriber import add_changelog_created
    event.object = testing.DummyResource(__provides__=IPasswordReset)
    add_changelog_created(event)
    assert changelog['/'].created is False


def test_add_changelog_created_with_parent(event, pool, changelog):
    from .subscriber import add_changelog_created
    pool.__name__ = 'parent'
    event.object.__parent__ = pool
    add_changelog_created(event)
    assert changelog['parent'].modified is True


def test_add_changelog_followed_with_has_no_follows(event, changelog):
    from .subscriber import add_changelog_followed
    event.new_version = None
    add_changelog_followed(event)
    assert changelog['/'].followed_by is None


def test_add_changelog_followed_with_has_follows(event, changelog):
    from .subscriber import add_changelog_followed
    event.new_version = testing.DummyResource()
    add_changelog_followed(event)
    assert changelog['/'].followed_by is event.new_version


class TestAddChangelogModified:

    @fixture
    def context(self, context):
        from BTrees.Length import Length
        root = testing.DummyResource()
        root.__changed_descendants_counter__ = Length()
        root['parent'] = testing.DummyResource()
        root['parent'].__changed_descendants_counter__ = Length()
        root['parent']['child'] = context
        return context

    def call_fut(self, event):
        from .subscriber import add_changelog_modified_and_descendants
        return add_changelog_modified_and_descendants(event)

    def test_set_modified_changelog(self, event, changelog):
        self.call_fut(event)
        assert changelog['/parent/child'].modified is True

    def test_dont_set_changed_descendants_for_context(self, event, changelog):
        self.call_fut(event)
        assert changelog['/parent/child'].changed_descendants is False

    def test_set_changed_descendants_changelog_for_parents(self, event,
                                                           changelog):
        self.call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is True

    def test_set_changed_descendants_only_once(self, event, changelog):
        """Stop iterating all parents if `changed_descendants` is already set"""
        changelog['/parent'] = \
            changelog['parent']._replace(changed_descendants=True)
        self.call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is False

    def test_increment_changed_descendants_counter_for_parents(self, event,
                                                               changelog):
        self.call_fut(event)
        assert changelog['/parent'].resource.\
                   __changed_descendants_counter__() == 1
        assert changelog['/'].resource.__changed_descendants_counter__() == 1


class TestAddChangelogBackrefs:

    @fixture
    def context(self, context):
        from BTrees.Length import Length
        root = testing.DummyResource()
        root.__changed_descendants_counter__ = Length()
        root['parent'] = testing.DummyResource()
        root['parent'].__changed_descendants_counter__ = Length()
        root['parent']['child'] = context
        context.__changed_backrefs_counter__ = Length()
        return context

    def call_fut(self, event):
        from .subscriber import add_changelog_backrefs
        return add_changelog_backrefs(event)

    def test_set_changed_backrefs_changelog(self, event, changelog):
        self.call_fut(event)
        assert changelog['/parent/child'].changed_backrefs is True

    def test_set_changed_backrefs_counter(self, event, changelog):
        self.call_fut(event)
        assert changelog['/parent/child'].resource.\
                   __changed_backrefs_counter__() == 1

    def test_set_changed_descendants_changelog_for_parents(self, event,
                                                           changelog):
        self.call_fut(event)
        assert changelog['/parent'].changed_descendants is True
        assert changelog['/'].changed_descendants is True

    def test_increment_changed_descendants_counter_for_parents(self, event,
                                                               changelog):
        self.call_fut(event)
        assert changelog['/parent'].resource.__changed_descendants_counter__() == 1
        assert changelog['/'].resource.__changed_descendants_counter__() == 1



@fixture
def mock_visibility(monkeypatch):
    from . import subscriber
    mock_visibility = Mock(spec=subscriber.get_visibility_change)
    monkeypatch.setattr(subscriber,
                        'get_visibility_change',
                        mock_visibility)
    return mock_visibility


def test_add_changelog_visibility(event, changelog, mock_visibility):
    from .subscriber import add_changelog_visibility
    mock_visibility.return_value = 'consealed'
    add_changelog_visibility(event)
    mock_visibility.assert_called_with(event)
    assert changelog['/'].visibility == 'consealed'


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from . import subscriber
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscriber.add_changelog_created.__name__ in handlers
    assert subscriber.add_changelog_followed.__name__ in handlers
    assert subscriber.add_changelog_modified_and_descendants.__name__ in handlers
    assert subscriber.add_changelog_backrefs.__name__ in handlers
    assert subscriber.add_changelog_visibility.__name__ in handlers
