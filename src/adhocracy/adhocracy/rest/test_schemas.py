import colander
import unittest
import pytest


class ResourceRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import ResourceRequestSchema
        return ResourceRequestSchema()

    def test_deserialize_valid_with_propertysheets(self):
        inst = self.make_one()
        assert inst.deserialize({"content_type": "X", "data": {"Y": "Z"}})

    def test_deserialize_valid_no_propertysheets(self):
        inst = self.make_one()
        assert inst.deserialize({"content_type": "X", "data": {}})

    def test_deserialize_no_valid_missing_contenttype(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({"data": {}})

    def test_deserialize_no_valid_missing_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({"content_type": {}})

    def test_deserialize_no_valid_wrong_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({"data": []})

    def test_deserialize_no_valid_missing_all(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})
