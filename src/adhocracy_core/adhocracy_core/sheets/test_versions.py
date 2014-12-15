import colander
from pyramid import testing
from pytest import fixture
from pytest import raises


class TestValidateLinearHistoryNoMerge:

    @fixture
    def last_version(self):
        return testing.DummyResource()

    @fixture
    def node(self):
        return testing.DummyResource()

    def _call_fut(self, node, value):
        from .versions import validate_linear_history_no_merge
        return validate_linear_history_no_merge(node, value)

    def test_value_length_lt_1(self, node):
        with raises(colander.Invalid) as err:
            self._call_fut(node, [])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_gt_1(self, node, last_version):
        with raises(colander.Invalid) as err:
            self._call_fut(node, [last_version, last_version])
        assert err.value.msg.startswith('No merge allowed')

    def test_value_length_eq_1(self, node, last_version):
        assert self._call_fut(node, [last_version]) is None


class TestValidateLinearHistoryNoFork:

    @fixture
    def tag(self):
        return testing.DummyResource()

    @fixture
    def context(self, tag):
        from adhocracy_core.interfaces import IItem
        context = testing.DummyResource(__provides__=IItem)
        context['LAST'] = tag
        return context

    @fixture
    def last_version(self, context):
        context['last_version'] = testing.DummyResource()
        return context['last_version']

    @fixture
    def request(self, registry, changelog):
        registry._transaction_changelog = changelog
        request = testing.DummyResource(registry=registry,
                                        validated={})
        return request

    @fixture
    def node(self, context, request):
        node = testing.DummyResource(bindings={})
        node.bindings['context'] = context
        node.bindings['request'] = request
        return node

    @fixture
    def mock_tag_sheet(self, tag, mock_sheet, registry):
        from adhocracy_core.testing import add_and_register_sheet
        from .tags import ITag
        mock_sheet.meta = mock_sheet.meta._replace(isheet=ITag)
        add_and_register_sheet(tag, mock_sheet, registry)
        return mock_sheet

    def _call_fut(self, node, value):
        from .versions import validate_linear_history_no_fork
        return validate_linear_history_no_fork(node, value)

    def test_value_last_version_is_last_version(
            self, node, last_version, mock_tag_sheet):
        mock_tag_sheet.get.return_value = {'elements': [last_version]}
        assert self._call_fut(node, [last_version]) is None

    def test_value_last_versions_is_not_last_version(
            self, node, last_version, mock_tag_sheet):
        mock_tag_sheet.get.return_value = {'elements': [last_version]}
        with raises(colander.Invalid) as err:
            self._call_fut(node, [object()])
        assert err.value.msg == 'No fork allowed - valid follows resources '\
                                'are: /last_version'


class TestVersionsSchema:

    @fixture
    def inst(self):
        from adhocracy_core.sheets.versions import VersionableSchema
        return VersionableSchema()

    def test_follows_validators(self, inst):
        from .versions import validate_linear_history_no_merge
        from .versions import validate_linear_history_no_fork
        field = inst['follows']
        validators = field.validator(object(), {}).validators
        assert validators == (validate_linear_history_no_merge,
                              validate_linear_history_no_fork,
                              )


class TestVersionsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versions_metadata
        return versions_metadata

    def test_create(self, meta, context):
        from adhocracy_core.sheets.versions import IVersions
        from adhocracy_core.sheets.versions import VersionsSchema
        from adhocracy_core.sheets.pool import PoolSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, PoolSheet)
        assert inst.meta.isheet == IVersions
        assert inst.meta.schema_class == VersionsSchema
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty(self, meta, context):
        context['child'] = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty_with_versionable(self, meta, context):
        from adhocracy_core.sheets.versions import IVersionable
        versionable = testing.DummyResource(__provides__=IVersionable)
        context['child'] = versionable
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [versionable]}


def test_includeme_register_version_sheet(config):
    from adhocracy_core.utils import get_sheet
    from adhocracy_core.sheets.versions import IVersions
    config.include('adhocracy_core.sheets.versions')
    context = testing.DummyResource(__provides__=IVersions)
    assert get_sheet(context, IVersions)


class TestVersionableSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.versions import versionable_metadata
        return versionable_metadata

    @fixture
    def context(self, context, mock_graph):
        context.__graph__ = mock_graph
        return context

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.versions import IVersionable
        from adhocracy_core.sheets.versions import VersionableSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IVersionable
        assert inst.meta.schema_class == VersionableSchema

    def test_get_empty(self, meta, context, mock_graph):
        inst = meta.sheet_class(meta, context)
        mock_graph.get_back_references_for_isheet.return_value = {}
        mock_graph.get_references_for_isheet.return_value = {}
        data = inst.get()
        assert list(data['follows']) == []
        assert list(data['followed_by']) == []

    def test_get_with_followed_by(self, meta, context, mock_graph):
        successor = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        mock_graph.get_back_references_for_isheet.return_value = {'follows': iter([successor])}
        data = inst.get()
        assert list(data['followed_by']) == [successor]

    def test_get_with_follows(self, meta, context, mock_graph):
        precessor = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        mock_graph.get_references_for_isheet.return_value = {'follows': iter([precessor])}
        data = inst.get()
        assert list(data['follows']) == [precessor]

    def test_set_with_followed_by(self, meta, context):
        inst = meta.sheet_class(meta, context)
        inst.set({'followed_by': iter([])})
        assert not 'followed_by' in inst._data


def test_includeme_register_versionable_sheet(config):
    from adhocracy_core.utils import get_sheet
    from adhocracy_core.sheets.versions import IVersionable
    config.include('adhocracy_core.sheets.versions')
    context = testing.DummyResource(__provides__=IVersionable)
    assert get_sheet(context, IVersionable)
