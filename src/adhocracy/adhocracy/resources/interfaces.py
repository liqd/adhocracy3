"""Interfaces for adhocarcy resources."""
from adhocracy.interfaces import IResource
from substanced.interfaces import IAutoNamingFolder
from zope.interface import taggedValue


class IPool(IResource, IAutoNamingFolder):

    """Folder in the object hierarchy.

    Namespace, structure and configure Fubels for a Participation Process.
    Additional TaggedValue: 'addable_content_interfaces'

    """

    taggedValue('content_class', 'adhocracy.folder.ResourcesAutolNamingFolder')
    taggedValue('basic_sheets',
                set(['adhocracy.sheets.name.IName',
                     'adhocracy.sheets.pool.IPool']))
    taggedValue('addable_content_interfaces',
                set(['adhocracy.resources.interfaces.IPool']))
    """ Set addable content types, class heritage is honored"""


class IFubelVersionsPool(IPool):

    """Pool for all VersionableFubels (DAG), tags and related Pools.

    Additional TaggedValue: 'fubel_type'

    """

    taggedValue('content_name', 'FubelVersionsPool')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName',
                 'adhocracy.sheets.tags.ITags',
                 'adhocracy.sheets.versions.IVersions',
                 'adhocracy.sheets.pool.IPool']))
    taggedValue('addable_content_interfaces', set([
                'adhocracy.resources.interfaces.IVersionableFubel',
                'adhocracy.resources.interfaces.ITag',
                ]))
    taggedValue('fubel_type',
                'adhocracy.resources.interfaces.IVersionableFubel')
    """Type of VersionableFubel for this VersionPool.
    Subtypes have to override.
    """


class IFubel(IResource):

    """Small object without versions and children."""

    taggedValue('content_name', 'Fubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName']))


class IVersionableFubel(IResource):

    """Versionable object, created during a Participation Process (mainly)."""

    taggedValue('content_name', 'VersionableFubel')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.INameReadOnly',
                 'adhocracy.sheets.versions.IVersionable']))


# Concrete Fubels and FubelVersionsPools

class IProposal(IVersionableFubel):

    """Versionable Fubel with Document propertysheet."""

    taggedValue('extended_sheets', set(
                ['adhocracy.sheets.document.IDocument']))


class IProposalVersionsPool(IFubelVersionsPool):

    """Proposal Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.interfaces.ITags',
         'adhocracy.resources.interfaces.IFubelVersionsPool']))
    taggedValue('fubel_content_type',
                'adhocracy.resources.interfaces.IProposal')


class ISection(IVersionableFubel):

    """Document section."""


class ISectionVersionsPool(IFubelVersionsPool):

    """Section Versions Pool."""

    taggedValue('addable_content_interfaces', set(
        ['adhocracy.resources.interfaces.ITags',
         'adhocracy.resources.interfaces.ISection']))
    taggedValue('fubel_type', 'adhocracy.resources.interfaces.ISection')
