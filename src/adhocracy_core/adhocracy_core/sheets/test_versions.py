import colander
from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark


class TestValidateLinearHistoryNoMerge:

    @fixture
    def last_version(self):
        return testing.DummyResource()

    @fixture
    def node(self):
        return testing.DummyResource()

    def call_fut(self, node, value):
        from .versions import validate_linear_history_no_merge
        return validate_linear_history_no_merge(node, value)

    def test_value_length_lt_1(self, node):
        with raises(colander.Invalid) as err:
            self.call_fut(node, [])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_gt_1(self, node, last_version):
        with raises(colander.Invalid) as err:
            self.call_fut(node, [last_version, last_version])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_eq_1(self, node, last_version):
        assert self.call_fut(node, [last_version]) is None


class TestValidateLinearHistoryNoFork:

    @fixture
    def node(self, node, kw):
        return node.bind(**kw)

    @fixture
    def mock_sheet(self, mock_sheet, registry_with_content):
        registry_with_content.content.get_sheet.return_value = mock_sheet
        return mock_sheet

    @fixture
    def last(self, context):
        last = testing.DummyResource()
        context['last_version'] = last
        return last

    @fixture
    def other(self, context):
        other = testing.DummyResource()
        context['other_version'] = other
        return other

    def call_fut(self, node, kw):
        from .versions import deferred_validate_linear_history_no_fork
        return deferred_validate_linear_history_no_fork(node, kw)

    def test_ignore_if_value_is_last_version(
            self, node, last, mock_sheet, kw):
        mock_sheet.get.return_value = {'LAST': last}
        assert self.call_fut(node, kw)(node, [last]) is None

    def test_raise_if_value_is_not_last_last_version(
            self, node, last, other, mock_sheet, kw):
        mock_sheet.get.return_value = {'LAST': last}
        with raises(colander.Invalid) as err:
            self.call_fut(node, kw)(node, [other]) is None
        assert err.value.msg == 'No fork allowed - valid follows resources '\
                                'are: /last_version'

    def test_batchmode_ignore_if_value_is_last(
            self, node, last, mock_sheet, changelog, request_, kw):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        assert self.call_fut(node, kw)(node, [last]) is None

    def test_batchmode_raise_if_value_is_not_last_last_version(
            self, node, last, other, mock_sheet, changelog, request_, kw):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        with raises(colander.Invalid) as err:
            self.call_fut(node, kw)(node, [other])
        assert err.value.msg == 'No fork allowed - valid follows resources '\
                                'are: /last_version'

    def test_batchmode_ingnore_if_last_version_created_in_transaction(
            self, node, last, other, mock_sheet, changelog, request_, kw):
        from adhocracy_core.utils import set_batchmode
        request_.registry.changelog = changelog
        set_batchmode(request_)
        mock_sheet.get.return_value = {'LAST': last}
        request_.registry.changelog['/last_version'] =\
            changelog['/last_version']._replace(created=True)
        assert self.call_fut(node, kw)(node, [other]) is None


class TestVersionsSchema:

    @fixture
    def inst(self):
        from adhocracy_core.sheets.versions import VersionableSchema
        return VersionableSchema()

    def test_follows_validators(self, inst, node, kw, mocker):
        from .versions import validate_linear_history_no_merge
        mock_val = mocker.patch('adhocracy_core.sheets.versions'
                                '.deferred_validate_linear_history_no_fork',
                                )
        validators = inst['follows'].validator(node, kw).validators
        assert validators == (validate_linear_history_no_merge,
                              mock_val.return_value)
        mock_val.assert_called_with(node, kw)


class TestVersionsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versions_meta
        return versions_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.pool import PoolSheet
        from .versions import IVersions
        from .versions import VersionsSchema
        inst = meta.sheet_class(meta, context, None)
        assert isinstance(inst, PoolSheet)
        assert inst.meta.isheet == IVersions
        assert inst.meta.schema_class == VersionsSchema
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self, meta, context):
        context['child'] = testing.DummyResource()
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() == {'elements': []}

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)


class TestVersionableSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versionable_meta
        return versionable_meta

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.versions import IVersionable
        from adhocracy_core.sheets.versions import VersionableSchema
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IVersionable
        assert inst.meta.schema_class == VersionableSchema

    def test_get_empty(self, meta, context, sheet_catalogs):
        inst = meta.sheet_class(meta, context, None)
        data = inst.get()
        assert list(data['follows']) == []

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)
