from pytest import fixture
from pytest import mark


def test_polarization_meta():
    from .relation import polarization_meta
    from .relation import IPolarization
    from .relation import IPolarizationVersion
    from .relation import IRelation
    meta = polarization_meta
    assert meta.iresource is IPolarization
    assert meta.iresource.isOrExtends(IRelation)
    assert meta.item_type == IPolarizationVersion
    assert meta.element_types == (IPolarizationVersion,)
    assert meta.use_autonaming
    assert meta.permission_create == 'create_comment'
    assert meta.is_implicit_addable is True


def test_polarizationversion_meta():
    from .relation import polarizationversion_meta
    from .relation import IPolarizationVersion
    from .relation import IRelationVersion
    import adhocracy_core.sheets.relation
    import adhocracy_core.sheets.comment
    meta = polarizationversion_meta
    assert meta.iresource is IPolarizationVersion
    assert meta.iresource.isOrExtends(IRelationVersion)
    assert meta.extended_sheets == (adhocracy_core.sheets.relation.IPolarization,
                                    )
    assert meta.permission_create == 'edit_comment'


def test_relationservice_meta():
    from .relation import relations_meta
    from .relation import IRelationsService
    from .relation import IRelation
    meta = relations_meta
    assert meta.iresource is IRelationsService
    assert meta.element_types == (IRelation,)
    assert meta.content_name == 'relations'


@mark.usefixtures('integration')
class TestPolarization:

    @fixture
    def context(self, pool):
        return pool

    def test_create_polarization(self, context, registry):
        from adhocracy_core.resources.relation import IPolarization
        res = registry.content.create(IPolarization.__identifier__, context)
        assert IPolarization.providedBy(res)

    def test_create_polarizationversion(self, context, registry):
        from adhocracy_core.resources.relation import IPolarizationVersion
        res = registry.content.create(IPolarizationVersion.__identifier__, context)
        assert IPolarizationVersion.providedBy(res)

    def test_create_relationsservice(self, context, registry):
        from adhocracy_core.resources.relation import IRelationsService
        from substanced.util import find_service
        res = registry.content.create(IRelationsService.__identifier__, context)
        assert IRelationsService.providedBy(res)
        assert find_service(context, 'relations')

    def test_add_relationsservice(self, context, registry):
        from adhocracy_core.resources.relation import add_relationsservice
        add_relationsservice(context, registry, {})
        assert context['relations']
