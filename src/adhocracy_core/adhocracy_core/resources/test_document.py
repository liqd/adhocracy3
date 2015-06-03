from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.document')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.rate')


class TestDocument:

    @fixture
    def meta(self):
        from .document import document_meta
        return document_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core.interfaces import ITag
        assert meta.iresource == resources.document.IDocument
        assert meta.element_types == [ITag,
                                      resources.paragraph.IParagraph,
                                      resources.document.IDocumentVersion,
                                      ]
        assert meta.item_type == resources.document.IDocumentVersion
        assert meta.permission_create == 'create_proposal'
        assert resources.comment.add_commentsservice in meta.after_creation
        assert resources.rate.add_ratesservice in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestDocumentVersion:

    @fixture
    def meta(self):
        from .document import document_version_meta
        return document_version_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource == resources.document.IDocumentVersion
        assert meta.extended_sheets == [sheets.document.IDocument,
                                        sheets.comment.ICommentable,
                                        sheets.rate.IRateable,
                                        sheets.image.IImageReference,
                                        ]
        assert meta.permission_create == 'edit_proposal'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
