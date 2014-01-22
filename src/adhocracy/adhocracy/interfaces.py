"""Basic Interfaces used by all packages."""
from substanced.interfaces import IPropertySheet
from zope.interface import Attribute


class IResourcePropertySheet(IPropertySheet):

    """Subclass of substancd PropertySheet."""

    iface = Attribute('The IProperty interface used to configure this Sheet.')
    key = Attribute('Internal dictionary key to store the schema data.')
    readonly = Attribute('Bool to indicate you should not set data.')
    createmandatory = Attribute('Bool to indicate you should set data when '
                                'creating a new resource.')

    def get_cstruct():
        """ Return a serialized dictionary representing the propertyt state."""
        pass

    def set_cstruct(cstruct):
        """ Accept ``cstruct``  and persist it to the context.

        (a serialized dictionary representing the property state)

        """
        pass
