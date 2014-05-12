import unittest

from pyramid import testing


#############
#  helpers  #
#############

class DummyFolder(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
        obj.__oid__ = 1

    def check_name(self, name):
        if name == 'invalid':
            raise ValueError
        return name


################
#  tests       #
################

class ResourceFactoryIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_add_root_element(self):
        from adhocracy.evolution import add_app_root_element
        self.config.include('substanced.content')
        self.config.include('adhocracy.registry')
        self.config.include('adhocracy.resources.pool')
        self.config.include('adhocracy.sheets.name')
        root = DummyFolder()
        add_app_root_element(root)
        assert 'adhocracy' in root

    def test_add_app_root_permissions(self):
        from adhocracy.evolution import add_app_root_permissions
        root = testing.DummyResource()
        root['adhocracy'] = testing.DummyResource()
        add_app_root_permissions(root)
        assert len(root['adhocracy'].__acl__) > 0

    def test_includeme_register_steps(self):
        from substanced.interfaces import IEvolutionSteps
        self.config.include('substanced.evolution')
        self.config.include('adhocracy.evolution')
        steps = self.config.registry.getUtility(IEvolutionSteps)
        assert 'adhocracy.evolution.add_app_root_element' in steps.names
        assert 'adhocracy.evolution.add_app_root_permissions' in steps.names
