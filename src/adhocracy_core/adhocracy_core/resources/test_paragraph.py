from pyramid import testing
from pytest import fixture
from pytest import mark


def test_paragraphversion_meta():
    from adhocracy_core import sheets
    from .paragraph import paragraphversion_meta
    from .paragraph import IParagraphVersion
    meta = paragraphversion_meta
    assert meta.iresource is IParagraphVersion
    assert meta.permission_create == 'edit_proposal'
    assert meta.extended_sheets == [sheets.document.IParagraph,
                                    sheets.comment.ICommentable,
                                    ]


def test_paragraph_meta():
    from .paragraph import paragraph_meta
    from .paragraph import IParagraphVersion
    from .paragraph import IParagraph
    from .comment import add_commentsservice

    from .tag import ITag
    from adhocracy_core import sheets
    meta = paragraph_meta
    assert meta.iresource is IParagraph
    assert meta.element_types == [ITag, IParagraphVersion]
    assert meta.item_type == IParagraphVersion
    assert meta.basic_sheets == [sheets.tags.ITags,
                                 sheets.versions.IVersions,
                                 sheets.pool.IPool,
                                 sheets.metadata.IMetadata,
                                 ]
    assert meta.permission_create == 'edit_proposal'
    assert meta.use_autonaming
    assert meta.autonaming_prefix == 'PARAGRAPH_'
    assert add_commentsservice in meta.after_creation


@mark.usefixtures('integration')
class TestParagraph:

    @fixture
    def context(self, pool):
        return pool

    def test_create_paragraph(self, context, registry):
        from adhocracy_core.resources.paragraph import IParagraph
        res = registry.content.create(IParagraph.__identifier__,
                                      parent=context)
        assert IParagraph.providedBy(res)

    def test_create_paragraphversion(self, context, registry):
        from adhocracy_core.resources.paragraph import IParagraphVersion
        res = registry.content.create(IParagraphVersion.__identifier__,
                                      parent=context)
        assert IParagraphVersion.providedBy(res)
