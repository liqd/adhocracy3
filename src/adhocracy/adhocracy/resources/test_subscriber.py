from adhocracy.interfaces import ChangelogMetadata
from pytest import mark
from pytest import fixture

from pyramid import testing


@fixture()
def event(transaction_changelog, context):
    registry = testing.DummyResource()
    registry._transaction_changelog = transaction_changelog
    event = testing.DummyResource(object=context, registry=registry)
    return event


class TestResourceCreatedAndAddedSubscriber:

    def _call_fut(self, event):
        from adhocracy.resources.subscriber import resource_created_and_added_subscriber
        return resource_created_and_added_subscriber(event)

    def test_call(self, event, transaction_changelog):
        self._call_fut(event)
        assert transaction_changelog['/'].created is True


class TestItemVersionCreated:

    def _call_fut(self, event):
        from adhocracy.resources.subscriber import itemversion_created_subscriber
        return itemversion_created_subscriber(event)

    def test_call_with_version_has_no_follows(self, event, transaction_changelog):
        event.new_version = None
        self._call_fut(event)
        assert transaction_changelog['/'].followed_by is None

    def test_call_with_version_has_follows(self, event, transaction_changelog):
        event.new_version = testing.DummyResource()
        self._call_fut(event)
        assert transaction_changelog['/'].followed_by is event.new_version


class TestResourceModifiedSubscriber:

    def _call_fut(self, event):
        from adhocracy.resources.subscriber import resource_modified_subscriber
        return resource_modified_subscriber(event)

    def test_call(self, event, transaction_changelog):
        self._call_fut(event)
        assert transaction_changelog['/'].modified is True


def test_create_transaction_changelog():
    from adhocracy.resources.subscriber import create_transaction_changelog
    changelog = create_transaction_changelog()
    changelog_metadata = changelog['/resource/path']
    assert isinstance(changelog_metadata, ChangelogMetadata)


def test_clear_transaction_changelog_exists(registry, transaction_changelog):
    from adhocracy.resources.subscriber import clear_transaction_changelog_after_commit_hook
    registry._transaction_changelog = transaction_changelog
    transaction_changelog['/'] = object()
    clear_transaction_changelog_after_commit_hook(True, registry)
    assert len(registry._transaction_changelog) == 0


def test_clear_transaction_changelog_does_not_exists(registry):
    from adhocracy.resources.subscriber import clear_transaction_changelog_after_commit_hook
    assert clear_transaction_changelog_after_commit_hook(True, registry) is None


def test_default_changelog_metadata():
    from adhocracy.resources.subscriber import changelog_metadata
    assert changelog_metadata.modified is False
    assert changelog_metadata.created is False
    assert changelog_metadata.followed_by is None
    assert changelog_metadata.resource is None


@fixture()
def integration(config):
    config.include('adhocracy.resources.subscriber')


@mark.usefixtures('integration')
def test_add_transaction_changelog(registry):
    assert hasattr(registry, '_transaction_changelog')


@mark.usefixtures('integration')
def test_register_subscriber(registry):
    from adhocracy.resources import subscriber
    handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
    assert subscriber.resource_created_and_added_subscriber.__name__ in handlers
    assert subscriber.itemversion_created_subscriber.__name__ in handlers
    assert subscriber.resource_modified_subscriber.__name__ in handlers
