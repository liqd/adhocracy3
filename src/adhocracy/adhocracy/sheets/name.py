"""Name Sheet."""
from zope.interface import provider
from zope.interface import taggedValue
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import Identifier


@provider(IIResourcePropertySheet)
class IName(ISheet):

    """Human readable resource Identifier, used to build object paths."""

    taggedValue('field:name', Identifier(default='', missing=colander.drop))


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IName, IIResourcePropertySheet),
                                    IResourcePropertySheet)
