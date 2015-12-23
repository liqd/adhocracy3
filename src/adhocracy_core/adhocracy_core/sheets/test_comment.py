from pyramid import testing
from pytest import fixture


def test_includeme_register_comment_sheet(config):
    from adhocracy_core.sheets.comment import IComment
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.comment')
    context = testing.DummyResource(__provides__=IComment)
    assert get_sheet(context, IComment)


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
    def inst(self, meta, context):
        return meta.sheet_class(meta, context)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from . import comment
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == comment.ICommentable
        assert inst.meta.schema_class == comment.CommentableSchema
        assert inst.meta.sheet_class == comment.CommentableSheet

    def test_get_empty(self, inst):
        data = inst.get()
        assert list(data['comments']) == []

    def test_get_with_comments(self, inst, sheet_catalogs, search_result):
        comment = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[comment])
        data = inst.get()
        assert list(data['comments']) == [comment]

    def test_set_with_comments(self, meta, context, sheet_catalogs):
        inst = meta.sheet_class(meta, context)
        inst.set({'comments': []})
        assert not 'comments' in getattr(context, inst._annotation_key)
