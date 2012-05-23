import json

from zope.schema import Tuple
from zope.schema import List
from zope.schema import Dict
from zope.schema.fieldproperty import FieldProperty


def _dict_to_db(python_dict):
    for k in python_dict:
        assert isinstance(k, str), u"All dictionary keys has to be strings"
    return json.dumps(python_dict)


_convert_to_db_map = {
                       Tuple: lambda x: json.dumps(x),
                       List: lambda x: json.dumps(x),
                       Dict: _dict_to_db,
                     }


_convert_to_python_map = {
                       Tuple: lambda x: tuple(json.loads(x)),
                       List: lambda x: json.loads(x),
                       Dict: lambda x: json.loads(x),
                     }


def python_to_db(zope_schema_field, python_value):
    """Convert the python value to a neo4j graphdb compatible value
       according to the zope_schema_field object type.
    """
    zope_schema_type = type(zope_schema_field)
    converter = _convert_to_db_map.get(zope_schema_type, None)
    if converter:
        return converter(python_value)
    else:
        return python_value


def db_to_python(zope_schema_field, graphdb_value):
    """Convert the graphdb value to a proper python value
       according to the zope_schema_field object type.
    """
    zope_schema_type = type(zope_schema_field)
    converter = _convert_to_python_map.get(zope_schema_type, None)
    if converter:
        return converter(graphdb_value)
    else:
        return graphdb_value


_marker = object()


class AdoptedFieldProperty(FieldProperty):
    """
       Fieldproperty decorator class that stores values with the
       IVector dbgraph api and works with adapters.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def _get_vector(self, inst):
        return inst.context

    def __get__(self, inst, klass):
        if inst is None:
            return self
        vector = self._get_vector(inst)
        value = vector.get_property(self.__name, _marker)
        field = self.__field
        if value is _marker:
            field = field.bind(vector)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
            return value
        else:
            return db_to_python(field, value)

    def __set__(self, inst, value):
        vector = self._get_vector(inst)
        field = self.__field.bind(vector)
        field.validate(value)
        if field.readonly and self.__name in vector.__dict__:
            raise ValueError(self.__name, 'field is readonly')
        value_db = python_to_db(field, value)
        vector.set_property(self.__name, value_db)
