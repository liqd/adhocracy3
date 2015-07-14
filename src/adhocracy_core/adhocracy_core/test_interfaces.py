import unittest

from adhocracy_core.interfaces import ISheet


class SheetToSheetUnitTests(unittest.TestCase):

    def test_create_valid(self):
        from adhocracy_core.interfaces import SheetToSheet as Reference
        # substanced standard tagged values
        assert Reference.getTaggedValue('source_integrity') is False
        assert Reference.getTaggedValue('target_integrity') is False
        assert Reference.getTaggedValue('source_ordered') is False
        assert Reference.getTaggedValue('target_ordered') is False
        # extra tagged values
        assert Reference.getTaggedValue('source_isheet') is ISheet
        assert Reference.getTaggedValue('source_isheet_field') == u''
        assert Reference.getTaggedValue('target_isheet') is ISheet

    def test_create_valid_custom_values(self):
        from adhocracy_core.interfaces import SheetToSheet
        from adhocracy_core.interfaces import ISheet

        class IA(ISheet):
            pass

        class Reference(SheetToSheet):
            source_integrity = True
            target_integrity = True
            target_ordered = True
            source_ordered = True
            source_isheet = IA
            source_isheet_field = u''
            target_isheet = IA

        # substanced standard tagged values
        assert Reference.getTaggedValue('source_integrity')
        assert Reference.getTaggedValue('target_integrity')
        assert Reference.getTaggedValue('source_ordered')
        assert Reference.getTaggedValue('target_ordered')
        # extra tagged values
        assert Reference.getTaggedValue('source_isheet') is IA
        assert Reference.getTaggedValue('source_isheet_field') == u''
        assert Reference.getTaggedValue('target_isheet') is IA


class TestNamedTuple:

    class ISample:
        pass

    class ISampleSheetA:
        pass

    class ISampleSheetB:
        pass

    def call_fut(self, typename, field_names, verbose=False, rename=False):
        from .interfaces import namedtuple
        return namedtuple(typename, field_names, verbose, rename)

    def make_one(self):
        meta_class = self.call_fut('ResourceMetadata', ['extended_sheets',
                                                        'after_creation'])
        meta = meta_class(extended_sheets=(self.ISampleSheetA,),
                          after_creation=())
        return meta


    def test_namedtuple(self):
        def after_creation_sample(self):
            pass

        meta = self.make_one()
        new_meta = meta._add(extended_sheets=(self.ISampleSheetB,),
                             after_creation=(after_creation_sample,))
        assert new_meta.extended_sheets == (self.ISampleSheetA, self.ISampleSheetB)
        assert new_meta.after_creation == (after_creation_sample,)
