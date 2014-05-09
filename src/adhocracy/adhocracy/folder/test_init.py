from pyramid import testing

import unittest


class ResourcesAutolNamingFolderUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, d=None):
        from . import ResourcesAutolNamingFolder
        return ResourcesAutolNamingFolder(d)

    def test_create(self):
        from adhocracy.interfaces import IAutoNamingManualFolder
        from zope.interface.verify import verifyObject
        inst = self._makeOne()
        assert verifyObject(IAutoNamingManualFolder, inst)

    def test_to_string_without_oid(self):
        from adhocracy.interfaces import IAutoNamingManualFolder
        inst = self._makeOne()
        wanted_str = '{0}:{1}'.format(IAutoNamingManualFolder.__identifier__,
                                      repr(inst))
        assert wanted_str == str(inst)

    def test_to_string_with_oid(self):
        from adhocracy.interfaces import IAutoNamingManualFolder
        inst = self._makeOne()
        inst.__oid__ = 1
        wanted_str = '{0}:{1}'.format(IAutoNamingManualFolder.__identifier__,
                                      str(1))
        assert wanted_str == str(inst)

    def test_next_name_empty(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        assert inst.next_name(ob) == '0'.zfill(7)
        assert inst.next_name(ob) == '1'.zfill(7)

    def test_next_name_nonempty(self):
        ob = testing.DummyResource()
        inst = self._makeOne({'nonintifiable': ob})
        assert inst.next_name(ob) == '0'.zfill(7)

    def test_next_name_nonempty_intifiable(self):
        ob = testing.DummyResource()
        inst = self._makeOne({'0000000': ob})
        assert inst.next_name(ob).startswith('0'.zfill(7) + '_20')

    def test_next_name_empty_prefix(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        assert inst.next_name(ob, prefix='prefix') == 'prefix' + '0'.zfill(7)
        assert inst.next_name(ob,) == '1'.zfill(7)

    def test_add(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add('name', ob)
        assert 'name' in inst

    def test_add_next(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add_next(ob)
        assert '0'.zfill(7) in inst

    def test_add_next_prefix(self):
        ob = testing.DummyResource()
        inst = self._makeOne()
        inst.add_next(ob, prefix='prefix')
        assert 'prefix' + '0'.zfill(7) in inst
