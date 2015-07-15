from pytest import mark
from pytest import fixture

class TestProposal:

    @fixture
    def meta(self):
        from .alexanderplatz import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        from .alexanderplatz import IProposalVersion
        assert meta.element_types == (IProposalVersion,)
        assert meta.item_type == IProposalVersion
        assert meta.permission_create == 'create_proposal'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta, context):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)


class TestProposalVersion:

    @fixture
    def meta(self):
        from .alexanderplatz import proposal_version_meta
        return proposal_version_meta

    def test_meta(self, meta):
        import adhocracy_core.sheets
        assert meta.extended_sheets == \
               (adhocracy_core.sheets.badge.IBadgeable,
                adhocracy_core.sheets.title.ITitle,
                adhocracy_core.sheets.description.IDescription,
                adhocracy_core.sheets.comment.ICommentable,
                adhocracy_core.sheets.rate.IRateable,
                adhocracy_core.sheets.geo.IPoint,
                )
        assert meta.permission_create == 'edit_proposal'

    @mark.usefixtures('integration')
    def test_create(self, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)

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
        from adhocracy_core.sheets.geo import ILocationReference
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource is resources.alexanderplatz.IProcess
        assert ILocationReference in meta.extended_sheets

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
