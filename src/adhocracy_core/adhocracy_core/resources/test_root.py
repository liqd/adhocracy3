from pyramid import testing
from pytest import fixture
from pytest import mark
from unittest.mock import Mock

def test_root_meta():
    from .root import root_meta
    from .root import IRootPool
    from .root import create_initial_content_for_app_root
    from .root import add_example_process
    meta = root_meta
    assert meta.iresource is IRootPool
    assert create_initial_content_for_app_root in meta.after_creation
    assert add_example_process in meta.after_creation


@fixture
def integration(config):
    config.include('pyramid_mailer.testing')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.subscriber')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.organisation')
    config.include('adhocracy_core.resources.badge')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.rate')
    config.include('adhocracy_core.resources.item')
    config.include('adhocracy_core.resources.paragraph')
    config.include('adhocracy_core.resources.document')
    config.include('adhocracy_core.resources.external_resource')
    config.include('adhocracy_core.rest')
    config.include('adhocracy_core.resources.geo')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.messaging')


@mark.usefixtures('integration')
class TestRoot:

    @fixture
    def request_(self, registry):
        request = testing.DummyResource()
        request._registry = registry
        return request

    def test_create_root_without_inital_content(self, registry):
        from adhocracy_core.resources.root import IRootPool
        assert registry.content.create(IRootPool.__identifier__,
                                       run_after_create=False)

    def test_create_root_with_initial_content(self, registry):
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.utils import find_graph
        from substanced.util import find_objectmap
        from substanced.util import find_catalog
        from substanced.util import find_service
        inst = registry.content.create(IRootPool.__identifier__)
        assert IRootPool.providedBy(inst)
        assert find_objectmap(inst) is not None
        assert find_graph(inst) is not None
        assert find_graph(inst)._objectmap is not None
        assert find_catalog(inst, 'system') is not None
        assert find_catalog(inst, 'adhocracy') is not None
        assert find_service(inst, 'principals', 'users') is not None
        assert find_service(inst, 'locations') is not None

    def test_create_root_with_acl(self, registry):
        from adhocracy_core.resources.root import IRootPool
        from substanced.util import get_acl
        from pyramid.security import Allow
        from pyramid.security import ALL_PERMISSIONS
        inst = registry.content.create(IRootPool.__identifier__)
        acl = get_acl(inst)
        assert (Allow, 'system.Anonymous', 'view') in acl
        assert (Allow, 'system.Anonymous', 'create_user') in acl
        assert (Allow, 'role:god', ALL_PERMISSIONS) == acl[0]

    def test_create_root_with_initial_god_user(self, registry, request_):
        from substanced.interfaces import IUserLocator
        from adhocracy_core.resources.root import IRootPool
        inst = registry.content.create(IRootPool.__identifier__)
        locator = registry.getMultiAdapter((inst, request_), IUserLocator)
        user_god = locator.get_user_by_login('god')
        assert not user_god is None
        assert user_god.password != ''
        assert user_god.email == 'sysadmin@test.de'

    def test_create_root_with_initial_god_user_with_custom_login(
            self,  registry, request_):
        from substanced.interfaces import IUserLocator
        from adhocracy_core.resources.root import IRootPool
        registry.settings['adhocracy.initial_login'] = 'custom'
        registry.settings['adhocracy.initial_password'] = 'password'
        registry.settings['adhocracy.initial_email'] = 'c@test.de'
        inst = registry.content.create(IRootPool.__identifier__)
        locator = registry.getMultiAdapter((inst, request_), IUserLocator)
        user_god = locator.get_user_by_login('custom')
        assert not user_god is None
        assert user_god.password != ''
        assert user_god.email == 'c@test.de'

    def test_create_root_with_initial_god_group(self, registry, request_):
        from substanced.util import find_service
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.utils import get_sheet
        inst = registry.content.create(IRootPool.__identifier__)
        groups = find_service(inst, 'principals', 'groups')
        group_gods = groups['gods']
        group_sheet = get_sheet(group_gods, IGroup)
        group_users = [x.__name__ for x in group_sheet.get()['users']]
        group_roles = group_sheet.get()['roles']
        assert group_users == ['0000000']
        assert group_roles == ['god']

    def test_create_root_with_example_process(self, registry):
        from adhocracy_core.resources.process import IProcess
        from .root import IRootPool
        inst = registry.content.create(IRootPool.__identifier__)
        assert IProcess.providedBy(inst['adhocracy'])

    def test_includeme_registry_add_default_group(self, registry, request_):
        from substanced.util import find_service
        from adhocracy_core.resources.root import IRootPool
        from adhocracy_core.sheets.principal import IGroup
        from adhocracy_core.utils import get_sheet
        inst = registry.content.create(IRootPool.__identifier__)
        groups = find_service(inst, 'principals', 'groups')
        group = groups['authenticated']
        group_sheet = get_sheet(group, IGroup)
        group_users = [x.__name__ for x in group_sheet.get()['users']]
        group_roles = group_sheet.get()['roles']
        assert group is not None
        assert group_roles == ['participant']


