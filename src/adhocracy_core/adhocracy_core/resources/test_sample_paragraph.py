from pyramid import testing
from pytest import fixture
from pytest import mark


def test_paragraphversion_meta():
    from .sample_paragraph import paragraphversion_meta
    from .sample_paragraph import IParagraphVersion
    meta = paragraphversion_meta
    assert meta.iresource is IParagraphVersion
    assert meta.permission_add == 'add_paragraphversion'


def test_paragraph_meta():
    from .sample_paragraph import paragraph_meta
    from .sample_paragraph import IParagraphVersion
    from .sample_paragraph import IParagraph
    from .tag import ITag
    meta = paragraph_meta
    assert meta.iresource is IParagraph
    assert meta.element_types == [ITag, IParagraphVersion]
    assert meta.item_type == IParagraphVersion
    assert meta.permission_add == 'add_paragraph'


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.sample_paragraph')
    config.include('adhocracy_core.resources.tag')


@mark.usefixtures('integration')
class TestParagraph:

    @fixture
    def context(self, pool):
        return pool

    def test_create_paragraph(self, context, registry):
        from adhocracy_core.resources.sample_paragraph import IParagraph
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': 'name1'}}
        res = registry.content.create(IParagraph.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert IParagraph.providedBy(res)

    def test_create_paragraphversion(self, context, registry):
        from adhocracy_core.resources.sample_paragraph import IParagraphVersion
        res = registry.content.create(IParagraphVersion.__identifier__,
                                      parent=context)
        assert IParagraphVersion.providedBy(res)
