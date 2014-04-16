import colander
import unittest
import pytest


class ResourceResponseSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import ResourceResponseSchema
        return ResourceResponseSchema()

    def test_serialize_no_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': '', 'path': ''}
        assert inst.serialize() == wanted

    def test_serialize_with_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': 'x', 'path': '/'}
        assert inst.serialize({'content_type': 'x', 'path': '/'}) == wanted


class ItemResponseSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import ItemResponseSchema
        return ItemResponseSchema()

    def test_serialize_no_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': '', 'path': '', 'first_version_path': ''}
        assert inst.serialize() == wanted

    def test_serialize_with_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': 'x', 'path': '/', 'first_version_path': '/v'}
        assert inst.serialize({'content_type': 'x', 'path': '/',
                               'first_version_path': '/v'}) == wanted


class POSTResourceRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import POSTResourceRequestSchema
        return POSTResourceRequestSchema()

    def test_deserialize_valid_with_propertysheets(self):
        inst = self.make_one()
        assert inst.deserialize({'content_type': 'X', 'data': {'Y': 'Z'}})

    def test_deserialize_valid_no_propertysheets(self):
        inst = self.make_one()
        assert inst.deserialize({'content_type': 'X', 'data': {}})

    def test_deserialize_no_valid_missing_contenttype(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'data': {}})

    def test_deserialize_no_valid_missing_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'content_type': {}})

    def test_deserialize_no_valid_wrong_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'data': []})

    def test_deserialize_no_valid_missing_all(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})



class POSTItemRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from .schemas import POSTItemRequestSchema
        return POSTItemRequestSchema()

    #FIXME test root_version deserialize with dummy objectmap


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
