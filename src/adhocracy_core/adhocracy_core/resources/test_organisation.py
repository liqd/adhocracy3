from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.resources.organisation')


class TestOrganisation:

    @fixture
    def meta(self):
        from .organisation import organisation_meta
        return organisation_meta

    def test_meta(self, meta):
        from .organisation import IOrganisation
        from .process import IProcess
        from adhocracy_core.interfaces import IPool
        assert meta.iresource is IOrganisation
        assert IOrganisation.isOrExtends(IPool)
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_organisation'
        assert meta.element_types == [IProcess]


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
