from pyramid import testing

import unittest


class SheetNameDummy(object):

    def __init__(*args):
        pass

    def get(self):
        return {'name': 'dummyname'}


def create_dummy_with_name_propertysheet(config):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.sheets.interfaces import IName
    from adhocracy.interfaces import IISheet
    from zope.interface import alsoProvides
    alsoProvides(IName, IISheet)
    config.registry.registerAdapter(SheetNameDummy,
                                    (IName, IISheet),
                                    IResourcePropertySheet)
    return testing.DummyResource(__provides__=IName)


class ResourcesAutolNamingFolderUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, d=None):
        from . import ResourcesAutolNamingFolder
        return ResourcesAutolNamingFolder(d)

    def test_next_name_versionable_empty(self):
        from adhocracy.resources.interfaces import IVersionableFubel
        ob = testing.DummyResource(__provides__=IVersionableFubel)
        inst = self._makeOne()
        assert inst.next_name(ob) == 'VERSION_' + '0'.zfill(7)

    def test_next_name_versionable_nonempty_intifiable(self):
        from adhocracy.resources.interfaces import IVersionableFubel
        ob = testing.DummyResource(__provides__=IVersionableFubel)
        inst = self._makeOne({'VERSION_0000000': ob})
        assert inst.next_name(ob).startswith('VERSION_' + '0'.zfill(7) + '_20')

    def test_next_name_versionable_nonempty_nonintifiable(self):
        from adhocracy.resources.interfaces import IVersionableFubel
        ob = testing.DummyResource(__provides__=IVersionableFubel)
        inst = self._makeOne({'abcd': ob})
        assert inst.next_name(ob) == 'VERSION_' + '0'.zfill(7)

    def test_next_name_other_noname_empty(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        assert inst.next_name(ob).startswith('20')

    def test_next_name_other_with_name_empty(self):
        ob = create_dummy_with_name_propertysheet(self.config)
        inst = self._makeOne()
        assert inst.next_name(ob) == 'dummyname'

    def test_next_name_other_with_name_nonempty(self):
        ob = create_dummy_with_name_propertysheet(self.config)
        inst = self._makeOne({'dummyname': ob})
        assert inst.next_name(ob).startswith('dummyname_20')

    def test_add_next_versionable_empty(self):
        from adhocracy.resources.interfaces import IVersionableFubel
        ob = testing.DummyResource(__provides__=IVersionableFubel)
        inst = self._makeOne()
        result = inst.add_next(ob)
        name = 'VERSION_' + '0'.zfill(7)
        assert ob.__name__ == name
        assert name in inst
        assert name == result
