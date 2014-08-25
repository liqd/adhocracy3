import unittest

from pyramid import testing
from pytest import fixture


def test_includeme_register_comment_sheet(config):
    from adhocracy_sample.sheets.comment import IComment
    from adhocracy.utils import get_sheet
    config.include('adhocracy_sample.sheets.comment')
    context = testing.DummyResource(__provides__=IComment)
    assert get_sheet(context, IComment)


class TestCommentableSheet:

    @fixture
    def meta(self):
        from adhocracy_sample.sheets.comment import commentable_meta
        return commentable_meta

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy.interfaces import IResourceSheet
        from adhocracy_sample.sheets.comment import ICommentable
        from adhocracy_sample.sheets.comment import CommentableSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == ICommentable
        assert inst.meta.schema_class == CommentableSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        data = inst.get()
        assert list(data['comments']) == []

    def test_get_with_comments(self, meta, context, mock_graph):
        comment = testing.DummyResource()
        inst = meta.sheet_class(meta, context)
        inst._graph = mock_graph
        mock_graph.get_back_references_for_isheet.return_value = {'refers_to': [comment]}
        data = inst.get()
        assert list(data['comments']) == [comment]

    def test_set_with_comments(self, meta, context):
        inst = meta.sheet_class(meta, context)
        inst.set({'comments': []})
        assert not 'comments' in inst._data
