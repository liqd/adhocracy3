import colander
from substanced.schema import (
    Schema,
    NameSchemaNode
    )
from substanced.interfaces import (
    IFolder,
    IAutoNamingFolder
)
from zope.interface import (
    Interface,
    Attribute,
    taggedValue,
)

from adhocracy3.schema import ReferenceSetSchemaNode

# Interface types

class IMarker(Interface):
    """Marker interface to represent a special type of object.
       It does not expose any attribute or method.
    """

class IContent(Interface):
    """Marker interface for adhocracy content objects
    """

class IPool(IContent, IFolder):
    """Folder to define a namespace for supergraph nodes
       and to provide services like catalog, workflow registry, ...
    """

class INode(IContent):
    """Marker interface representing a supergraph node"""


class IPropertySheetMarker(Interface):
    """Marker interface with tagged value "schema" to
       reference a colander schema class.

       The colander schema should define the facade to work with
       IContent objects.

       To set/get the data you can adapt to IPropertySheet objects.
    """

    taggedValue("schema", "substanced.schema.Schema")


# Basic Pools

class INodeContainer(IPool):
    """Pool for all versions and tags of one node versions darc
       or other node containers that are part of the essence.

       Children:

           versions = INodeVersions object

           tags = INodeTags object
    """

    content_type = Attribute('Addable node contenttype, '
                             'has to implement INode and IVersionable')


class INodeVersions(IPool, IAutoNamingFolder):
    """Pool to store all node versions
    """

class INodeTags(IPool):
    """Pool to store tag nodes to reference specific node versions
    """

# Name Data

class NameSchema(Schema):

    name = NameSchemaNode()


class IName(IPropertySheetMarker):

    taggedValue("schema", "adhocracy3.resources.interfaces.NameSchema")


# Concrete Nodes

class IProposal(INode):
    """Proposal node"""


class IProposalContainer(INodeContainer):
    """Proposal node container"""


# Versionable Data

class IVersionable(IPropertySheetMarker):
    """Marker interface representing a node with version data"""

    taggedValue("schema", "adhocracy3.resources.interfaces.VersionableSchema")

class IForkable(IVersionable):
    """Marker interface representing a forkable node with version data"""


class VersionableSchema(Schema):

    follows = ReferenceSetSchemaNode(essence_refs=True,
                                     default=[],
                                     missing=[],
                                     interface=IVersionable,
                                     )

# Text Data

class IText(IPropertySheetMarker):
    """Marker interfaces representing a node with text data """

    taggedValue("schema", "adhocracy3.resources.interfaces.TextSchema")


class TextSchema(Schema):

    title =  colander.SchemaNode(colander.String())

    content =  colander.SchemaNode(colander.String())
