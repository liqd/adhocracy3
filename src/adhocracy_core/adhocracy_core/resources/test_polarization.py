from pytest import fixture
from pytest import mark


def test_polarization_meta():
    from .polarization import polarization_meta
    from .polarization import IPolarization
    from .polarization import IPolarizationVersion
    meta = polarization_meta
    assert meta.iresource is IPolarization
    assert meta.item_type == IPolarizationVersion
    assert meta.element_types == (IPolarizationVersion,)
    assert meta.use_autonaming
    assert meta.permission_create == 'create_comment'


def test_polarizationversion_meta():
    from .polarization import polarizationversion_meta
    from .polarization import IPolarizationVersion
    import adhocracy_core.sheets.polarization
    import adhocracy_core.sheets.comment
    meta = polarizationversion_meta
    assert meta.iresource is IPolarizationVersion
    assert meta.extended_sheets == (adhocracy_core.sheets.polarization.IPolarization,
                                    adhocracy_core.sheets.comment.ICommentable,
                                    )
    assert meta.permission_create == 'edit_comment'


def test_polarizationservice_meta():
    from .polarization import polarizations_meta
    from .polarization import IPolarizationsService
    from .polarization import IPolarization
    meta = polarizations_meta
    assert meta.iresource is IPolarizationsService
    assert meta.element_types == (IPolarization,)
    assert meta.content_name == 'polarizations'


@mark.usefixtures('integration')
class TestPolarization:

    @fixture
    def context(self, pool):
        return pool

    def test_create_polarization(self, context, registry):
        from adhocracy_core.resources.polarization import IPolarization
        res = registry.content.create(IPolarization.__identifier__, context)
        assert IPolarization.providedBy(res)

    def test_create_polarizationversion(self, context, registry):
        from adhocracy_core.resources.polarization import IPolarizationVersion
        res = registry.content.create(IPolarizationVersion.__identifier__, context)
        assert IPolarizationVersion.providedBy(res)

    def test_create_polarizationsservice(self, context, registry):
        from adhocracy_core.resources.polarization import IPolarizationsService
        from substanced.util import find_service
        res = registry.content.create(IPolarizationsService.__identifier__, context)
        assert IPolarizationsService.providedBy(res)
        assert find_service(context, 'polarizations')

    def test_add_polarizationsservice(self, context, registry):
        from adhocracy_core.resources.polarization import add_polarizationsservice
        add_polarizationsservice(context, registry, {})
        assert context['polarizations']
