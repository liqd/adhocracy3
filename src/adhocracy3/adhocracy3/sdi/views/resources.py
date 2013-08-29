from pyramid.httpexceptions import HTTPFound

from substanced.sdi import mgmt_view
from substanced.form import FormView
from substanced.interfaces import IFolder

from adhocracy3.resources.interfaces import (
    NameSchema
)

#
#   SDI "add" view for resources
#

@mgmt_view(
    context=IFolder,
    name='add_node',
    tab_title='Add Node',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddNodeView(FormView):
    title = 'Add Node'
    contenttype = 'adhocracy3.resources.interfaces.INode'
    schema = NameSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        content = registry.content.create(self.contenttype, **appstruct)
        self.context[name] = content
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

@mgmt_view(
    context=IFolder,
    name='add_nodecontainer',
    tab_title='Add NodeContainer',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddNodeContainerView(AddNodeView):
    title = 'Add NodeContainer'
    schema = NameSchema()
    contenttype = 'adhocracy3.resources.interfaces.INodeContainer'


@mgmt_view(
    context=IFolder,
    name='add_pool',
    tab_title='Add Pool',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddPoolView(AddNodeView):
    title = 'Add Pool'
    schema = NameSchema()
    contenttype = 'adhocracy3.resources.interfaces.IPool'
