from zope.schema.fieldproperty import FieldProperty


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
        if value is _marker:
            field = self.__field.bind(vector)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        vector = self._get_vector(inst)
        field = self.__field.bind(vector)
        field.validate(value)
        if field.readonly and self.__name in vector.__dict__:
            raise ValueError(self.__name, 'field is readonly')
        vector.set_property(self.__name, value)
