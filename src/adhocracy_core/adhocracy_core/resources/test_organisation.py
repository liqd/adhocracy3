from pyramid import testing
from pytest import mark
from pytest import fixture
from unittest.mock import Mock


class TestOrganisation:

    @fixture
    def meta(self):
        from .organisation import organisation_meta
        return organisation_meta

    def test_meta(self, meta):
        import adhocracy_core.sheets
        from .organisation import IOrganisation
        from .organisation import enabled_ordering
        from .organisation import sdi_organisation_columns
        from .process import IProcess
        from adhocracy_core.interfaces import IPool
        assert meta.iresource is IOrganisation
        assert IOrganisation.isOrExtends(IPool)
        assert meta.is_sdi_addable
        assert meta.sdi_column_mapper == sdi_organisation_columns
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_organisation'
        assert meta.element_types == (IProcess,
                                      IOrganisation,
                                      )
        assert meta.basic_sheets == \
               (adhocracy_core.sheets.name.IName,
                adhocracy_core.sheets.title.ITitle,
                adhocracy_core.sheets.pool.IPool,
                adhocracy_core.sheets.metadata.IMetadata,
                adhocracy_core.sheets.workflow.IWorkflowAssignment,
                adhocracy_core.sheets.localroles.ILocalRoles,
                adhocracy_core.sheets.description.IDescription,
                adhocracy_core.sheets.image.IImageReference,
                adhocracy_core.sheets.notification.IFollowable,
                )
        assert meta.extended_sheets == \
            (adhocracy_core.sheets.asset.IHasAssetPool,)
        assert enabled_ordering in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)


def test_enable_ordering(context, mocker):
    from .pool import Pool
    context.set_order = mocker.Mock(spec=Pool.set_order)
    context.__oid__ = 0
    context['child'] = context.clone()
    from .organisation import enabled_ordering
    enabled_ordering(context, None)
    assert context.set_order.call_args[0] == (['child'],)
    assert context.set_order.call_args[1] == {'reorderable': True}


class TestSdiOrganisationColums:

    @fixture
    def request_(self, context, registry_with_content):
        request = testing.DummyRequest(context=context)
        request.registry = registry_with_content
        return request

    def call_fut(self, *args, **kwargs):
        from .organisation import sdi_organisation_columns
        return sdi_organisation_columns(*args, **kwargs)

    def test_sdi_organisation_columns_no_context(self, request_):
        result = self.call_fut(None, None, request_, [])
        assert result == [
            {'name': 'Type','value': ''},
            {'name': 'Title','value': ''},
        ]

    def test_sdi_user_columns_organisation(self, request_, resource_meta):
        from .organisation import IOrganisation
        context = testing.DummyResource(__provides__=IOrganisation)
        request_.registry.content.resources_meta[IOrganisation] = \
            resource_meta._replace(content_name='Organisation')
        result = self.call_fut(None, context, request_, [])
        assert result == [
            {'name': 'Type','value': 'Organisation'},
            {'name': 'Title','value': ''},
        ]

    def test_sdi_user_columns_process(self, request_, resource_meta):
        from .process import IProcess
        context = testing.DummyResource(__provides__=IProcess)
        request_.registry.content.resources_meta[IProcess] = \
            resource_meta._replace(content_name='Process')
        request_.registry.content.get_sheet_field = Mock(return_value='Test')
        result = self.call_fut(None, context, request_, [])
        assert result == [
            {'name': 'Type','value': 'Process'},
            {'name': 'Title','value': 'Test'},
        ]
