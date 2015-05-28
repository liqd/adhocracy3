from pytest import fixture
from pytest import mark


@fixture
def integration(config, pool_graph_catalog):
    config.include('pyramid_mailer.testing')
    config.include('adhocracy_meinberlin')


def test_root_meta():
    from adhocracy_core.resources.root import root_meta
    from adhocracy_core.resources.root import \
        create_initial_content_for_app_root
    from .root import create_initial_content_for_meinberlin
    from .root import meinberlin_root_meta
    assert create_initial_content_for_meinberlin not in root_meta.after_creation
    assert create_initial_content_for_meinberlin in\
           meinberlin_root_meta.after_creation
    assert create_initial_content_for_app_root in\
           meinberlin_root_meta.after_creation


@mark.usefixtures('integration')
def test_create_initial_content_for_meinberlin(pool_graph_catalog, registry):
    from adhocracy_core.utils import get_sheet_field
    from adhocracy_core.resources.organisation import IOrganisation
    from adhocracy_core.resources.geo import IMultiPolygon
    from adhocracy_core.resources.geo import add_locations_service
    import adhocracy_core.sheets.geo
    from .root import IProcess
    from .root import create_initial_content_for_meinberlin
    root = pool_graph_catalog
    add_locations_service(root, registry, {})
    create_initial_content_for_meinberlin(root, registry, {})
    assert IOrganisation.providedBy(root['organisation'])
    kiezkasse =  root['organisation']['kiezkasse']
    assert IProcess.providedBy(kiezkasse)
    kiezregion = get_sheet_field(kiezkasse,
                                 adhocracy_core.sheets.geo.ILocationReference,
                                 'location'
                                 )
    assert IMultiPolygon.providedBy(kiezregion)



