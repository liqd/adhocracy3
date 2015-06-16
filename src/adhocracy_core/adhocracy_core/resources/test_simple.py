from pyramid import testing
from pytest import fixture
from pytest import mark


def test_simple_meta():
    import adhocracy_core.sheets
    from .simple import simple_meta
    from .simple import ISimple
    meta = simple_meta
    assert meta.iresource is ISimple
    assert meta.basic_sheets == [adhocracy_core.sheets.name.IName,
                                 adhocracy_core.sheets.title.ITitle,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 ]
    assert meta.permission_create == 'create_simple'
    assert meta.permission_edit == 'edit'


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources')


@mark.usefixtures('integration')
class TestSimple:

    @fixture
    def context(self, pool):
        return pool

    def test_create_simple(self, context, registry):
        from adhocracy_core.resources.simple import ISimple
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': 'name1'}}
        res = registry.content.create(ISimple.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert ISimple.providedBy(res)

