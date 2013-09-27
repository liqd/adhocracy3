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
from adhocracy import (
    contents,
    propertysheets,
)


######################
#  Adhocracy Content #
######################


# Basic Pools


@content(
    # content type: has to resolve to content interface class
    'adhocracy.contents.interfaces.IPool',
    add_view='add_pool',
    factory_type = 'pool',
    # addable content types, class heritage is honored
    addable_content_interfaces = ["adhocracy.contents.interfaces.IPool"],
    # make this addable if supertype is addable
    is_implicit_addable = True
    # view_permission
    # edit_permission
    # node_content_type
    )
@implementer(contents.interfaces.IPool,
             propertysheets.interfaces.IName)
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
@implementer(contents.interfaces.INodeVersions)
def versions(context):
    content = RandomAutoNamingFolder()
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


@content(
    'adhocracy.contents.interfaces.INodeTags',
    factory_type = 'tags',
    addable_content_interfaces = ["adhocracy.contents.interfaces.INode"],
    )
@implementer(contents.interfaces.INodeTags)
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
@implementer(contents.interfaces.INode,
             propertysheets.interfaces.INameReadonly,
             propertysheets.interfaces.IVersionable)
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
@implementer(contents.interfaces.INodeContainer,
             propertysheets.interfaces.IName)
def container(context):
    content = Folder()
    node_content_type =\
        contents.interfaces.INodeContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(container).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                contents.interfaces.INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                contents.interfaces.INodeTags.__identifier__, context)
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
@implementer(contents.interfaces.IProposal,
             propertysheets.interfaces.INameReadonly,
             propertysheets.interfaces.IDocument,
             propertysheets.interfaces.IVersionable)
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
@implementer(contents.interfaces.INodeContainer, propertysheets.interfaces.IName)
def proposalcontainer(context):
    content = Folder()
    node_content_type =\
        contents.interfaces.IProposalContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(proposalcontainer).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                contents.interfaces.INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                contents.interfaces.INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content


@content(
    'adhocracy.contents.interfaces.IParagraph',
    add_view='add_paragraph',
    factory_type = 'paragraph',
    is_implicit_addable = True
    )
@implementer(propertysheets.interfaces.IParagraph,
             propertysheets.interfaces.INameReadonly,
             propertysheets.interfaces.IText,
             propertysheets.interfaces.IVersionable)
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
@implementer(contents.interfaces.INodeContainer,
             propertysheets.interfaces.IName)
def paragraphcontainer(context):
    content = Folder()
    node_content_type =\
        contents.interfaces.IParagraphContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(paragraphcontainer).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                contents.interfaces.INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                contents.interfaces.INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content
