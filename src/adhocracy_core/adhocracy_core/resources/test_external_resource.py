from pyramid import testing
from pytest import fixture
from pytest import mark


def test_external_resource_meta():
    from .external_resource import external_resource_meta
    from .external_resource import IExternalResource
    from .external_resource import add_ratesservice
    from .external_resource import add_commentsservice
    import adhocracy_core.sheets
    meta = external_resource_meta
    assert meta.iresource is IExternalResource
    assert meta.permission_create == 'create_external'
    assert meta.is_implicit_addable
    assert meta.extended_sheets == (adhocracy_core.sheets.comment.ICommentable,)
    assert add_ratesservice in meta.after_creation
    assert add_commentsservice in meta.after_creation


@mark.usefixtures('integration')
class TestExternalResource:

    @fixture
    def context(self, pool):
        return pool

    def test_create_external_resource(self, context, registry):
        from adhocracy_core.resources.external_resource import IExternalResource
        from adhocracy_core.sheets.name import IName
        appstructs = {IName.__identifier__: {'name': 'name1'}}
        res = registry.content.create(IExternalResource.__identifier__,
                                      appstructs=appstructs,
                                      parent=context)
        assert IExternalResource.providedBy(res)
