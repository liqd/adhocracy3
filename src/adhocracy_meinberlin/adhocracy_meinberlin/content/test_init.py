from pytest import fixture
from pyramid import testing


class TestMeinBerlinResourceContentRegistry:

    def test_create(self):
        from adhocracy_core.content import ResourceContentRegistry
        from . import MeinBerlinResourceContentRegistry
        inst = MeinBerlinResourceContentRegistry(object())
        assert isinstance(inst, ResourceContentRegistry)

    def test_includeme_overrides_content_registry(self, config, registry):
        from . import includeme
        from . import MeinBerlinResourceContentRegistry
        old_content = testing.DummyResource(dummy_attribute='a')
        registry.content = old_content
        includeme(config)
        new_content = registry.content
        assert isinstance(new_content, MeinBerlinResourceContentRegistry)
        assert new_content.dummy_attribute == old_content.dummy_attribute


class TestMeinBerlinResourceContentRegistryCanAddResource:

    @fixture
    def resource_meta(self, resource_meta):
        return resource_meta._replace(permission_create='create')

    @fixture
    def version_meta(self, resource_meta):
        from adhocracy_meinberlin.resources.bplan import IProposalVersion
        return resource_meta._replace(iresource=IProposalVersion,
                                      permission_create='create_version')

    @fixture
    def item_meta(self, resource_meta):
        from adhocracy_meinberlin.resources.bplan import IProposal
        return resource_meta._replace(iresource=IProposal,
                                      permission_create='create_item')

    @fixture
    def inst(self, registry, resource_meta, item_meta, version_meta):
        from . import MeinBerlinResourceContentRegistry
        inst = MeinBerlinResourceContentRegistry(registry)
        item_meta = resource_meta._replace(iresource=item_meta.iresource,
                                           permission_create='create_item')
        version_meta = resource_meta._replace(iresource=version_meta.iresource,
                                              permission_create='create_version')
        inst.resources_meta = {item_meta.iresource: item_meta}
        inst.resources_meta_addable = {version_meta.iresource: [version_meta]}
        return inst

    @fixture
    def item(self):
        from adhocracy_meinberlin.resources.bplan import IProposal
        return testing.DummyResource(__provides__=IProposal)

    @fixture
    def version(self):
        from adhocracy_meinberlin.resources.bplan import IProposalVersion
        return testing.DummyResource(__provides__=IProposalVersion)

    def test_true_if_create_permission(self, inst, context, request_,
                                       resource_meta, mock):
        request_.has_permission = mock.MagicMock(return_value=True)
        assert inst.can_add_resource(request_, resource_meta, context)
        request_.has_permission.assert_called_with('create', context)

    def test_false_if_no_create_permission(self, inst, context, request_,
                                           resource_meta, mock):
        request_.has_permission = mock.MagicMock(return_value=False)
        assert not inst.can_add_resource(request_, resource_meta, context)
        request_.has_permission.assert_called_with('create', context)

    def test_true_if_create_permission_item_and_only_empty_version(
            self, inst, item, version, request_, mock, item_meta, version_meta):
        request_.has_permission = mock.MagicMock(return_value=True)
        item['VERSION_0'] = version
        assert inst.can_add_resource(request_, version_meta, item)
        request_.has_permission.assert_called_with('create_item', item)

    def test_false_if_create_permission_item_and_only_non_empty_version(
            self, inst, item, version, request_, mock, version_meta, resource_meta):
        request_.has_permission = mock.MagicMock(return_value=False)
        item['VERSION_0'] = version
        item['VERSION_0']._sheet_dummy = {}
        assert not inst.can_add_resource(request_, version_meta, item)
        request_.has_permission.assert_called_with('create_version', item)

    def test_false_if_create_permission_item_and_empty_version(
            self, inst, item, version, request_, mock, version_meta, resource_meta):
        request_.has_permission = mock.MagicMock(return_value=False)
        item['VERSION_0'] = version
        item['VERSION_1'] = version.clone(__provides__=version.__provides__,
                                          _sheet_dummy={})
        assert not inst.can_add_resource(request_, version_meta, item)
        request_.has_permission.assert_called_with('create_version', item)

