from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from mock import Mock



class TestLocalRole:

    @fixture
    def inst(self):
        from .localroles import LocalRole
        return LocalRole()

    @fixture
    def context(self, pool):
        return pool

    @fixture
    def groups(self, context, service):
        context['principals'] = service
        context['principals']['groups'] = service.clone()
        return context['principals']['groups']

    def test_create(self, inst):
        import colander
        assert inst['principal'].missing is colander.required
        assert inst['roles'].missing is colander.required
        assert inst.missing is colander.required

    def test_create_principal_validator(self, inst, context, groups):
        from adhocracy_core.resources.principal import IGroup
        groups['group'] = testing.DummyResource(__provides__=IGroup)
        groups['non_group'] = testing.DummyResource()
        inst = inst.bind(context=context)
        assert inst['principal'].validator.choices == ['group:group']

    def test_create_principal_widget(self, inst, context, groups):
        from adhocracy_core.resources.principal import IGroup
        groups['group'] = testing.DummyResource(__provides__=IGroup)
        groups['non_group'] = testing.DummyResource()
        inst = inst.bind(context=context)
        assert inst['principal'].widget.values == [('group:group', 'group')]

    def test_deserialize_non_acl_role(self, inst):
        from colander import Invalid
        with raises(Invalid):
            inst.deserialize({'principal': 'group1', 'roles': ['WRONG']})

    def test_deserialize(self, inst):
        assert inst.deserialize({'principal': 'group1', 'roles': ['admin']})\
               == {'principal': 'group1', 'roles': ['role:admin']}

    def test_serialize(self, inst):
        assert inst.serialize({'principal': 'group1', 'roles': ['role:admin']})\
               == {'principal': 'group1', 'roles': ['admin']}


class TestLocalRolesSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.localroles import local_roles_meta
        return local_roles_meta

    def test_meta(self, meta):
        from . import localroles
        assert meta.isheet == localroles.ILocalRoles
        assert meta.schema_class == localroles.LocalRolesSchema
        assert meta.readable is True
        assert meta.editable is True
        assert meta.creatable is False
        assert meta.permission_edit == 'manage_sheet_local_roles'
        assert meta.permission_view == 'manage_sheet_local_roles'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context, mocker):
        mocker.patch('adhocracy_core.sheets.localroles.get_local_roles',
                     magic_spec=True,
                     return_value={})
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'local_roles': []}

    def test_get_with_roles(self, meta, context, mocker):
        mocker.patch('adhocracy_core.sheets.localroles.get_local_roles',
                     magic_spec=True,
                     return_value={'userid': {'role:admin'}})
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'local_roles': [{'principal': 'userid',
                                               'roles': ['role:admin']}]}

    def test_set_empty(self, meta, context, registry, mocker):
        set_roles = mocker.patch('adhocracy_core.sheets.localroles.'
                                 'set_local_roles',
                                 magic_spec=True)
        inst = meta.sheet_class(meta, context, registry)
        inst.set({})
        assert not set_roles.called

    def test_set_roles(self, meta, context, registry, mocker):
        set_roles = mocker.patch('adhocracy_core.sheets.localroles.'
                                 'set_local_roles',
                                 magic_spec=True)
        inst = meta.sheet_class(meta, context, registry)
        inst.set({'local_roles': [{'principal': 'userid',
                                   'roles': ['role:admin']}]})
        set_roles.assert_called_with(inst.context, {'userid': {'role:admin'}},
                                     registry)

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)

