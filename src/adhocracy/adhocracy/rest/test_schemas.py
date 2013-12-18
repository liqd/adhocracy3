import colander
import unittest
import pytest


class POSTResourceRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import POSTResourceRequestSchema
        return POSTResourceRequestSchema()

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


class OPTIONResourceResponeSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import OPTIONResourceResponseSchema
        return OPTIONResourceResponseSchema()

    def test_create_valid_no_propertysheets_and_no_addables(self):
        inst = self.make_one()
        wanted =\
            {'GET': {'request_body': {},
                     'request_querystring': {},
                     'response_body': {'content_type': '', 'data': {},
                                       'path': ''}},
             'HEAD': {},
             'OPTION': {},
             'POST': {'request_body': [],
                      'response_body': {'content_type': '', 'path': ''}},
             'PUT': {'request_body': {'data': {}},
                     'response_body': {'content_type': '', 'path': ''}}}
        assert inst.serialize() == wanted
