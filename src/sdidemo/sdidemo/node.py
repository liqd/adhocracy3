
import colander

from persistent import Persistent

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from substanced.content import content
from substanced.sdi import mgmt_view
from substanced.property import PropertySheet
from substanced.schema import (
    Schema,
    NameSchemaNode,
    )
from substanced.form import FormView


class NodeSchema(Schema):
    name = colander.SchemaNode(
        colander.String(),
    )

class NodePropertySheet(PropertySheet):
    schema = NodeSchema()

@content(
    'Node',
    name = 'Node',
    add_view = 'add_node',
    propertysheets=(
        ('Basic', NodePropertySheet),
        ),
    )
class Node(Persistent):
    def __init__(self, name):
        self.__name__ = name
        self.name = name

@view_config(
    renderer = 'json',
    context = Node,
)
def nodeRestView(context, request):
    return {
        'name': context.name,
      }

@mgmt_view(
    name='add_node',
    tab_title='Add Node',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddNodeView(FormView):
    title = 'Add Node'
    schema = NodeSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        node = self.request.registry.content.create('Node', **appstruct)
        self.context[node.__name__] = node
        return HTTPFound(
            self.request.mgmt_path(self.context, '@@contents'))
