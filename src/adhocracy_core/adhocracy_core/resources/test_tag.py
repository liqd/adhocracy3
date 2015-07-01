from pyramid import testing
from pytest import fixture
from pytest import mark


def test_tag_meta():
    from .tag import tag_meta
    from .tag import ITag
    import adhocracy_core.sheets
    meta = tag_meta
    assert meta.iresource is ITag
    assert meta.basic_sheets==[adhocracy_core.sheets.name.IName,
                               adhocracy_core.sheets.metadata.IMetadata,
                               adhocracy_core.sheets.tags.ITag,
                               ]
    assert meta.permission_create == 'create_tag'


@mark.usefixtures('integration')
class TestTag:

    @fixture
    def context(self, pool):
        return pool

    def test_create_tag(self, context, registry):
        from adhocracy_core.resources.tag import ITag
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': 'name1'}}
        res = registry.content.create(ITag.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert ITag.providedBy(res)
