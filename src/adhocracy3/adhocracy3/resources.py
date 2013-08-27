import colander
import deform.widget

from persistent import Persistent

from substanced.content import content
from substanced.folder import Folder 
from substanced.property import PropertySheet
from substanced.schema import (
    Schema,
    NameSchemaNode
    )
from substanced.util import renamer

#Basic Node classes

class NodeSchema(Schema):
    """Basic Supergraph Node"""
    name = NameSchemaNode()


class NodePropertySheet(PropertySheet):
    schema = NodeSchema()

class Node(Folder):

    name = renamer()

class PoolSchema(NodeSchema):
    """Pool for other Nodes"""
    pass

class PoolPropertySheet(PropertySheet):
    schema = PoolSchema()

@content(
    'Pool',
    add_view='add_pool',
    propertysheets=(
        ('Basic', PoolPropertySheet),
        ),
    )
class Pool(Node):
    elements = colander.SchemaNode(
        colander.Set(),
        Node
    )

# Node Pools

@content(
    'Instances',
    add_view='add_instances',
    propertysheets=(
        ('Basic', PoolPropertySheet),
        ),
    )
class Instances(Pool):
    """Pool for instances"""
    pass

@content(
    'Instance',
    add_view='add_instance',
    propertysheets=(
        ('Basic', PoolPropertySheet),
        ),
    )
class Instance(Pool):
    """Pool for participation processes"""
    pass

class ProcessSchema(PoolSchema):
    elements = colander.SchemaNode(
        colander.Set(),
        PoolSchema)

@content(
    'Process',
    add_view='add_process',
    propertysheets=(
        ('Basic', PoolPropertySheet),
        ),
    )
class Process(Pool):
    """Concrete participation process"""
    elements = 


