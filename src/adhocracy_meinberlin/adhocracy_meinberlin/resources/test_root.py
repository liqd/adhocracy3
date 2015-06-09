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
    import adhocracy_core.resources.root
    from .root import add_example_process
    from .root import meinberlin_root_meta
    assert add_example_process  not in root_meta.after_creation
    assert add_example_process in meinberlin_root_meta.after_creation
    assert adhocracy_core.resources.root.add_example_process in\
        meinberlin_root_meta.after_creation
    assert create_initial_content_for_app_root in\
           meinberlin_root_meta.after_creation


@mark.usefixtures('integration')
def test_add_example_process(pool_graph_catalog, registry):
    from adhocracy_core.utils import get_sheet_field
    from adhocracy_core.resources.organisation import IOrganisation
    from adhocracy_core.resources.geo import IMultiPolygon
    from adhocracy_core.resources.geo import add_locations_service
    import adhocracy_core.sheets.geo
    from adhocracy_meinberlin import resources
    from .root import add_example_process
    root = pool_graph_catalog
    add_locations_service(root, registry, {})
    add_example_process(root, registry, {})
    assert IOrganisation.providedBy(root['organisation'])
    kiezkasse =  root['organisation']['kiezkasse']
    assert resources.kiezkassen.IProcess.providedBy(kiezkasse)
    kiezregion = get_sheet_field(kiezkasse,
                                 adhocracy_core.sheets.geo.ILocationReference,
                                 'location'
                                 )
    assert IMultiPolygon.providedBy(kiezregion)
    bplan =  root['organisation']['bplan']
    assert resources.bplan.IProcess.providedBy(bplan)



