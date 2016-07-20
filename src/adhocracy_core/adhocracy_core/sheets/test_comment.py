from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import mark


@mark.usefixtures('integration')
def test_includeme_register_comment_sheet(config):
    from adhocracy_core.sheets.comment import IComment
    context = testing.DummyResource(__provides__=IComment)
    assert config.registry.content.get_sheet(context, IComment)


@fixture
def mock_catalogs(monkeypatch, mock_catalogs) -> Mock:
    from . import comment
    monkeypatch.setattr(comment, 'find_service', lambda x, y: mock_catalogs)
    mock_catalogs.get_index_value = Mock(return_value=0)
    return mock_catalogs


class TestDeferredDefaultCommentCount:

    def call_fut(self, *args):
        from .comment import deferred_default_comment_count
        return deferred_default_comment_count(*args)

    def test_deferred_default_comment_count(
        self, config, node, kw, mock_catalogs, mocker):
        kw['context'] = Mock()
        mock_catalogs.get_index_value.return_value = 1
        result = self.call_fut(node, kw)
        mock_catalogs.get_index_value.assert_called_with(kw['context'],
                                                         'comments')


class TestCommentableSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.comment import commentable_meta
        return commentable_meta

    @fixture
    def context(self, pool, service):
        pool['comments'] = service
        return pool

    @fixture
    def inst(self, meta, context, registry):
        return meta.sheet_class(meta, context, registry)

    def test_meta(self, meta):
        from . import comment
        assert meta.isheet == comment.ICommentable
        assert meta.schema_class == comment.CommentableSchema

    def test_create(self, inst, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst, context, mock_catalogs):
        data = inst.get()
        assert data['post_pool'] == context['comments']
        assert data['comments_count'] == 0

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
