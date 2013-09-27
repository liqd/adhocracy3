from zope.interface import (
    Interface,
    taggedValue,
)
from substanced.interfaces import (
    IFolder,
    IAutoNamingFolder
)
from substanced.folder import Folder


# Basic adhocracy content

class IContent(Interface):
    """Marker interface for adhocracy content objects
    """

    # TODO
    #  A tagged value "add_permission" sets the permission
    #  to create this content object and add it to the object hierarchy.
    # (in addition to the "addable_content_interfaces"  settings)
    # taggedValue("add_permission", "add-content")

    # A perm permission to list folder contents, view content meta data, search
    # taggedValue("view_permission", "view-content")


class IContentFolder(IContent, IFolder):
    """Marker interface for adhocracy content objects
    """


class IContentItem(IContent):
    """Marker interface for adhocracy content objects
    """


# Basic Pools

class IPool(IContentFolder):
    """Folder to define a namespace for supergraph nodes
       and to provide services like catalog, workflow registry, ...
   """
    # contenty_type_id = IPool.__identifier__ # autogenererated, substanced content type id
    taggedValue("propertysheet_interfaces", ["adhocracy.propertysheets.interfaces.IName"]),
    taggedValue("content_name", "Pool") # modifiable name TODO
    taggedValue("content_class", Folder) # class
    taggedValue("addable_content_interfaces",
                ["adhocracy.contents.interfaces.IPool"])  # addable content types, class heritage is honored
    taggedValue("is_implicit_addable", True) # make this addable if supertype is addable
    taggedValue("add_view", 'add_adhocracy.contents.interfaces.IPool') # add view for substanced sdi,
    #node_content_type TODO


class INodeContainer(IPool):
    """Pool for all versions and tags of one node versions darc
       or other node containers that are part of the essence.

       Children:

           _versions = INodeVersions object

           _tags = INodeTags object

       A tagged value "node_content_type" to set the type of node
       addable to this container.
    """

    taggedValue("node_content_type", "adhocracy.interfaces.INode")


class INodeVersions(IPool, IAutoNamingFolder):
    """Pool to store all node versions
    """


class INodeTags(IPool):
    """Pool to store tag nodes to reference specific node versions
    """

# Basic Node


class INode(IContentItem):
    """Marker interface representing a supergraph node"""


# Concrete Nodes


class IProposal(INode):
    """Proposal node"""


class IProposalContainer(INodeContainer):
    """Proposal node container"""

    taggedValue("node_content_type", "adhocracy.contents.interfaces.IProposal")


class IParagraph(INode):
    """Paragraph of documents"""


class IParagraphContainer(INodeContainer):
    """IParagraph DAG"""

    taggedValue("node_content_type", "adhocracy.interfaces.IParagraph")
