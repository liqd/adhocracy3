from zope.interface import (
    implementer,
    directlyProvides,
    implementedBy,
    )
from pyramid.threadlocal import get_current_registry
from substanced.content import content
from substanced.folder import (
    Folder,
    RandomAutoNamingFolder,
)
from adhocracy.propertysheets.interfaces import (
     IName,
     INameReadonly,
     IVersionable,
     IDocument,
     IText,
)
from adhocracy.contents.interfaces import (
     IPool,
     INodeContainer,
     INodeVersions,
     INodeTags,
     INode,
     IProposal,
     IProposalContainer,
     IParagraph,
     IParagraphContainer,
)

#######################
##  Adhocracy Content #
#######################


## Basic Pools


@content(
    # content interface/type: has to resolve to content interface class
    'adhocracy.contents.interfaces.IPool',
    # propertysheets that can be adapted to set/get data
    propertysheet_interfaces = [IName],
    # modifiable name TODO
    content_name = "Pool",
    # class
    #content_class = Folder,
    # view to make this content addable with sdi
    add_view='add_pool',
    # factory identifier
    factory_type = 'pool',
    # addable content types, class heritage is honored
    addable_content_interfaces = ["adhocracy.contents.interfaces.IPool"],
    # make this addable if supertype is addable
    is_implicit_addable = True
    # node_content_type TODO
    )
@implementer(IPool,
             IName)
def pool(context):
    content = Folder()
    # Set directly provided interfaces.
    # The implementer decorator does not work with functions
    # in python 3. So we have to declare the provided interfaces manually.
    directlyProvides(content, implementedBy(pool).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.INodeVersions',
    factory_type = 'versions',
    addable_content_interfaces = ["adhocracy.contents.interfaces.INode"],
    )
@implementer(INodeVersions)
def versions(context):
    content = RandomAutoNamingFolder()
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.INodeTags',
    factory_type = 'tags',
    addable_content_interfaces = ["adhocracy.contents.interfaces.INode"],
    )
@implementer(INodeTags)
def tags(context):
    content = Folder()
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


# Basic Node


@content(
    'adhocracy.contents.interfaces.INode',
    add_view='add_node',
    factory_type = 'node',
    is_implicit_addable = True
    )
@implementer(INode,
             INameReadonly,
             IVersionable)
def node(context):
    content = Folder()
    directlyProvides(content, implementedBy(node).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.INodeContainer',
    add_view='add_nodecontainer',
    factory_type = 'container',
    addable_content_interfaces =
        ["adhocracy.contents.interfaces.INodeContainer"],
    is_implicit_addable = True
    )
@implementer(INodeContainer,
             IName)
def container(context):
    content = Folder()
    node_content_type =\
        INodeContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(container).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content


# Concrete Nodes


@content(
    'adhocracy.contents.interfaces.IProposal',
    add_view='add_proposal',
    factory_type = 'proposal',
    is_implicit_addable = True
    )
@implementer(IProposal,
             INameReadonly,
             IDocument,
             IVersionable)
def proposal(context):
    content = Folder()
    directlyProvides(content, implementedBy(proposal).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.IProposalContainer',
    add_view='add_proposalcontainer',
    factory_type = 'proposalcontainer',
    addable_content_interfaces =
        ["adhocracy.contents.interfaces.IProposalContainer"],
    is_implicit_addable = True
    )
@implementer(INodeContainer, IName)
def proposalcontainer(context):
    content = Folder()
    node_content_type =\
        IProposalContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(proposalcontainer).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content


@content(
    'adhocracy.contents.interfaces.IParagraph',
    add_view='add_paragraph',
    factory_type = 'paragraph',
    is_implicit_addable = True
    )
@implementer(IParagraph,
             INameReadonly,
             IText,
             IVersionable)
def paragraph(context):
    content = Folder()
    directlyProvides(content, implementedBy(paragraph).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.IParagraphContainer',
    add_view='add_paragraphcontainer',
    factory_type = 'paragraphcontainer',
    addable_content_interfaces =
        ["adhocracy.contents.interfaces.IParagraphContainer"],
    is_implicit_addable = True
    )
@implementer(INodeContainer,
             IName)
def paragraphcontainer(context):
    content = Folder()
    node_content_type =\
        IParagraphContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(paragraphcontainer).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content
