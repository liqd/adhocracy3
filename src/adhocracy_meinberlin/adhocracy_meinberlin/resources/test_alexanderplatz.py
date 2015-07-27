from pytest import mark
from pytest import fixture

class TestDocument:

    @fixture
    def meta(self):
        from .alexanderplatz import document_meta
        return document_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core.interfaces import ITag
        from .alexanderplatz import IDocument
        from .alexanderplatz import IDocumentVersion
        assert meta.iresource == IDocument
        assert meta.element_types == (ITag,
                                      resources.paragraph.IParagraph,
                                      IDocumentVersion
                                      )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

class TestDocumentVersion:

    @fixture
    def meta(self):
        from .alexanderplatz import document_version_meta
        return document_version_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        from .alexanderplatz import IDocumentVersion
        assert meta.iresource == IDocumentVersion
        assert meta.extended_sheets == (sheets.document.IDocument,
                                        sheets.comment.ICommentable,
                                        sheets.badge.IBadgeable,
                                        sheets.rate.IRateable,
                                        sheets.image.IImageReference,
                                        sheets.title.ITitle,
                                        sheets.geo.IPoint
                                        )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

class TestProcess:

    @fixture
    def meta(self):
        from .alexanderplatz import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.process import IProcess
        from adhocracy_core.sheets import workflow
        from adhocracy_core.sheets.geo import ILocationReference
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource is resources.alexanderplatz.IProcess
        assert meta.extended_sheets == (workflow.IStandard, ILocationReference,)

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
