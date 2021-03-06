import unittest

from adhocracy_core.utils import to_dotted_name


class ResourceUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy_core.resources.base import Base
        return Base()

    def test_create(self):
        from pyramid.interfaces import ILocation
        from zope.interface.verify import verifyObject
        inst = self.make_one()
        assert ILocation.providedBy(inst)
        assert verifyObject(ILocation, inst)

    def test_add_attribute(self):
        inst = self.make_one()
        inst._test_attribute = None
        assert inst._test_attribute is None

    def test_to_string_without_oid_and_iresource(self):
        inst = self.make_one()
        inst_class = inst.__class__
        non_iresource = object()
        wanted_str = '{0} oid: {1} name: {2}'.format(to_dotted_name(non_iresource.__class__),
                                                     'None',
                                                     'None')
        assert wanted_str == inst_class.__repr__(non_iresource)

    def test_to_string_with_oid_and_name(self):
        inst = self.make_one()
        inst.__oid__ = 1
        inst.__name__ = None
        wanted_str = '{0} oid: {1} name: {2}'.format(to_dotted_name(inst.__class__),
                                           str(1),
                                           'None')
        assert wanted_str == str(inst)

    def test_to_string_with_iresource(self):
        from adhocracy_core.interfaces import IResource
        from zope.interface import directlyProvides
        inst = self.make_one()
        directlyProvides(inst, IResource)
        wanted_str = '{0} oid: {1} name: {2}'.format(IResource.__identifier__,
                                                     'None',
                                                     'None')
        assert wanted_str == str(inst)
