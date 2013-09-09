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
from adhocracy import interfaces


######################
#  Adhocracy Content #
######################


# Basic Pool

@content(
    # content type: has to resolve to content interface class
    'adhocracy.interfaces.IPool',
    add_view='add_pool',
    factory_type = 'pool',
    # addable content types, class heritage is honored
    addable_content_interfaces = ["adhocracy.interfaces.IPool"],
    # make this addable if supertype is addable
    is_implicit_addable = True
    )
@implementer(interfaces.IPool, interfaces.IName)
def pool(context):
    content = Folder()
    # Set directly provided interfaces.
    # The implementer decorator does not work with functions
    # in python 3. So we have to declare the provided interfaces manually.
    directlyProvides(content, implementedBy(pool).interfaces())
    return content

# Basic Node

@content(
    'adhocracy.interfaces.INodeVersions',
    factory_type = 'versions',
    addable_content_interfaces = ["adhocracy.interfaces.INode"],
    )
@implementer(interfaces.INodeVersions)
def versions(context):
    content = RandomAutoNamingFolder()
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


@content(
    'adhocracy.interfaces.INodeTags',
    factory_type = 'tags',
    addable_content_interfaces = ["adhocracy.interfaces.INode"],
    )
@implementer(interfaces.INodeTags)
def tags(context):
    content = Folder()
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


@content(
    'adhocracy.interfaces.INode',
    add_view='add_node',
    factory_type = 'node',
    is_implicit_addable = True
    )

@implementer(interfaces.INode, interfaces.IVersionable)
def node(context):
    content = Folder()
    directlyProvides(content, implementedBy(node).interfaces())
    return content


@content(
    'adhocracy.interfaces.INodeContainer',
    add_view='add_nodecontainer',
    factory_type = 'container',
    addable_content_interfaces =
        ["adhocracy.interfaces.INodeContainer"],
    is_implicit_addable = True
    )
@implementer(interfaces.INodeContainer, interfaces.IName)
def container(context):
    content = Folder()
    node_content_type =\
        interfaces.INodeContainer.getTaggedValue('node_content_type')
    directlyProvides(content, implementedBy(container).interfaces())
    registry = get_current_registry()
    content["_versions"] = registry.content.create(\
                                interfaces.INodeVersions.__identifier__, context)
    content["_tags"] = registry.content.create(\
                                interfaces.INodeTags.__identifier__, context)
    content["_versions"].add_next(registry.content.create(node_content_type,
                                                          context))
    return content
