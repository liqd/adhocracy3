import unittest


class ResourceUnitTest(unittest.TestCase):

    def make_one(self):
        from . import Resource
        return Resource()

    def test_create(self):
        from adhocracy.interfaces import IResource
        from zope.interface.verify import verifyObject
        inst = self.make_one()
        assert IResource.providedBy(inst)
        assert verifyObject(IResource, inst)

    def test_add_attribute(self):
        inst = self.make_one()
        inst._test_attribute = None
        assert inst._test_attribute is None

    def test_to_string_without_oid(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one()
        wanted_str = '{0}:{1}'.format(IResource.__identifier__, repr(inst))
        assert wanted_str == str(inst)

    def test_to_string_with_oid(self):
        from adhocracy.interfaces import IResource
        inst = self.make_one()
        inst.__oid__ = 1
        wanted_str = '{0}:{1}'.format(IResource.__identifier__, str(1))
        assert wanted_str == str(inst)
