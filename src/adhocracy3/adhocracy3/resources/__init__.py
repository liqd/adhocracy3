from zope.interface import (
    implementer,
    directlyProvides,
    implementedBy,
    )
from substanced.content import content
from substanced.folder import (
    Folder,
    RandomAutoNamingFolder,
)
from adhocracy3.resources import interfaces


###############
#  Resources  #
###############


# Basic Pool

@content(
    # has to resolve to content interface class
    'adhocracy3.resources.interfaces.IPool',
    add_view='add_pool',
    factory_type = 'pool',
    # addable content types, class heritage is honored
    addable_content_interfaces = ["adhocracy3.resources.interfaces.IPool"],
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
    'adhocracy3.resources.interfaces.INodeContainer',
    add_view='add_nodecontainer',
    factory_type = 'container',
    addable_content_interfaces =
        ["adhocracy3.resources.interfaces.INodeContainer"],
    is_implicit_addable = True
    )
@implementer(interfaces.INodeContainer, interfaces.IName)
def container(context):
    content = Folder()
    directlyProvides(content, implementedBy(container).interfaces())
    return content


@content(
    'adhocracy3.resources.interfaces.INodeVersions',
    factory_type = 'versions',
    addable_content_interfaces = ["adhocracy3.resources.interfaces.INode"],
    )
@implementer(interfaces.INodeVersions)
def versions(context):
    content = RandomAutoNamingFolder
    directlyProvides(content, implementedBy(versions).interfaces())
    return content


@content(
    'adhocracy3.resources.interfaces.INode',
    add_view='add_node',
    factory_type = 'node',
    is_implicit_addable = True
    )
@implementer(interfaces.INode, interfaces.IVersionable)
def node(context):
    content = Folder()
    directlyProvides(content, implementedBy(node).interfaces())
    return content


############
#  config  #
############

def includeme(config): # pragma: no cover
    config.include('.adapters')
