from pyramid.httpexceptions import HTTPFound

from substanced.sdi import mgmt_view
from substanced.form import FormView
from substanced.interfaces import (
    IFolder,
    IAutoNamingFolder,
)
from substanced.schema import Schema

from adhocracy.propertysheets.interfaces import (
    NameSchema
)

#
#   SDI "add" views for adhocracy content
#

class AddPoolBaseView(FormView):
    title = 'Add Ressource'
    contenttype = 'adhocracy.interfaces.IContent'
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


class AddNodeBaseView(FormView):
    title = 'Add Ressource'
    contenttype = 'adhocracy.interfaces.INode'
    schema = Schema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        content = registry.content.create(self.contenttype, **appstruct)
        self.context.add_next(content)
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

# basic nodes

@mgmt_view(
    context=IAutoNamingFolder,
    name='add_node',
    tab_title='Add Node',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddNodeView(AddNodeBaseView):
    title = 'Add Node'
    contenttype = 'adhocracy.interfaces.INode'


@mgmt_view(
    context=IFolder,
    name='add_nodecontainer',
    tab_title='Add NodeContainer',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddNodeContainerView(AddPoolBaseView):
    title = 'Add NodeContainer'
    contenttype = 'adhocracy.interfaces.INodeContainer'


@mgmt_view(
    context=IFolder,
    name='add_pool',
    tab_title='Add Pool',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddPoolView(AddPoolBaseView):
    title = 'Add Pool'
    contenttype = 'adhocracy.interfaces.IPool'

# concrete nodes

@mgmt_view(
    context=IAutoNamingFolder,
    name='add_proposal',
    tab_title='Add Proposal',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddProposalView(AddNodeBaseView):
    title = 'Add Proposal'
    contenttype = 'adhocracy.interfaces.IProposal'


@mgmt_view(
    context=IFolder,
    name='add_proposalcontainer',
    tab_title='Add ProposalContainer',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddProposalContainerView(AddPoolBaseView):
    title = 'Add ProposalContainer'
    contenttype = 'adhocracy.interfaces.IProposalContainer'
    name='add_proposal',
    tab_title='Add Proposal',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,


@mgmt_view(
    context=IAutoNamingFolder,
    name='add_paragraph',
    tab_title='Add Paragraph',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddParagraphView(AddNodeBaseView):
    title = 'Add Paragraph'
    contenttype = 'adhocracy.interfaces.IParagraph'


@mgmt_view(
    context=IFolder,
    name='add_paragraphcontainer',
    tab_title='Add ParagraphContainer',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddParagraphContainerView(AddPoolBaseView):
    title = 'Add ParagraphContainer'
    contenttype = 'adhocracy.interfaces.IParagraphContainer'
    name='add_paragraph',
    tab_title='Add Paragraph',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
