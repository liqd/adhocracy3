from substanced.interfaces import IPropertySheet
from zope.interface import Attribute


class IResourcePropertySheet(IPropertySheet):
    iface = Attribute('The IProperty interface used to configure this Sheet.')
    key = Attribute('Internal dictionary key to store the schema data.')
    readonly = Attribute('Bool to allow setting data.')

    def get_cstruct():
        """ Return a serialized dictionary representing the propertyt state"""
        pass

    def set_cstruct(cstruct):
        """ Accept ``cstruct`` (a serialized dictionary representing the
        property state) and persist it to the context.

        """
        pass
