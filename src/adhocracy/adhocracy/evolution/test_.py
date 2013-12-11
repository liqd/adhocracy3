

############
#  helper  #
############

class DummyFolder(dict):
    __acl__ = []


################
#  test steps  #
################

def test_add_root_element(config):
    from adhocracy.evolution import add_app_root_element
    config.include("substanced.content")
    config.include("adhocracy.resources")
    root = DummyFolder()
    add_app_root_element(root)
    assert "adhocracy" in root


def test_add_app_root_permissions():
    from adhocracy.evolution import add_app_root_permissions
    root = DummyFolder()
    root["adhocracy"] = DummyFolder()
    add_app_root_permissions(root)
    assert len(root["adhocracy"].__acl__) > 0


####################
#  test includeme  #
####################

def test_includeme_register_steps(config):
    from substanced.interfaces import IEvolutionSteps
    config.include("substanced.evolution")
    config.include("adhocracy.evolution")
    steps = config.registry.getUtility(IEvolutionSteps)
    assert 'adhocracy.evolution.add_app_root_element' in steps.names
    assert 'adhocracy.evolution.add_app_root_permissions' in steps.names
