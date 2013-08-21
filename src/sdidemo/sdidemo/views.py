import random
import string
import time

import colander
import deform

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.response import Response

from substanced.sdi import mgmt_view
from substanced.form import FormView
from substanced.interfaces import IFolder
from substanced.util import (
    oid_of,
    find_catalog,
    )

from .resources import (
    Document,
    DocumentSchema,
    BinderSchema,
    )

#
#   Default "retail" view
#
@view_config(
    renderer='templates/splash.pt',
)
def splash_view(request):
    manage_prefix = request.registry.settings.get(
        'substanced.manage_prefix',
        '/manage')
    return {'manage_prefix': manage_prefix}

#
#   "Retail" view for documents.
#
@view_config(
    context=Document,
    renderer='templates/document.pt',
    )
def document_view(context, request):
    return {'title': context.title,
            'body': context.body,
            'master': get_renderer(
                'templates/master.pt').implementation(),
            }




#
#   SDI "add" view for documents
#
@mgmt_view(
    context=IFolder,
    name='add_document',
    tab_title='Add Document',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
)
class AddDocumentView(FormView):
    title = 'Add Document'
    schema = DocumentSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        document = registry.content.create('Document', **appstruct)
        document.__creator__ = oid_of(self.request.user)
        self.context[name] = document
        return HTTPFound(
            self.request.mgmt_path(self.context, '@@contents'))


class Person(colander.Schema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Integer(),
                              validator=colander.Range(0,200))
class People(colander.SequenceSchema):
    person = Person()
class Schema(colander.Schema):
    people = People(
        widget=deform.widget.SequenceWidget(orderable=True)
    )

@mgmt_view(
    context=IFolder,
    name='paulie',
    tab_title='Add Document',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
)
class PaulieView(FormView):
    title = 'Paulie Form'
    schema = Schema()
    buttons = ('add',)

#from substanced.sdi import LEFT, RIGHT
#
#@mgmt_view(
#    name='tab_1',
#    tab_title='Tab 1',
#    renderer='templates/tab.pt'
#    )
#def tab_1(context, request):
#    return {}
#
#
#@mgmt_view(
#    name='tab_2',
#    tab_title='Tab 2',
#    renderer='templates/tab.pt',
#    tab_before='tab_1'
#    )
#def tab_2(context, request):
#    return {}
#
#
#@mgmt_view(
#    name='tab_3',
#    tab_title='Tab 3',
#    renderer='templates/tab.pt',
#    tab_near=RIGHT
#    )
#def tab_3(context, request):
#    return {}
#
#
#@mgmt_view(
#    name='tab_4',
#    tab_title='Tab 4',
#    renderer='templates/tab.pt',
#    tab_near=LEFT
#    )
#def tab_4(context, request):
#    return {}
#
#
#@mgmt_view(
#    name='tab_5',
#    tab_title='Tab 5',
#    renderer='templates/tab.pt',
#    tab_near=LEFT
#    )
#def tab_5(context, request):
#    return {}


# Demonstration of overriding a content registration
from zope.interface import implementer
from substanced.interfaces import IFolder
from substanced.folder import Folder
from substanced.sdi import mgmt_view
from substanced.sdi.views.folder import AddFolderView
from substanced.content import content
from substanced.sdi.views.folder import folder_contents_views, FolderContents

#@folder_contents_views()
#class MyFolderView(FolderContents):
#    def get_options(self):
#
#        return dict(
#            editable=False,
#            enableAddRow=False,
#            enableCellNavigation=True,
#            asyncEditorLoading=True,
#            forceFitColumns=True,
#            rowHeight=85,
#            )


@content(
    'Folder',
    icon='icon-folder-close',
    add_view='my_add_folder',
)
@implementer(IFolder)
class MyFolder(Folder):

    def send_email(self):
        pass

@mgmt_view(
    context=IFolder,
    name='my_add_folder',
    tab_condition=False,
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt'
)
class MyAddFolderView(AddFolderView):

    def before(self, form):
        # Perform some custom work before validation
        pass

@mgmt_view(
    name='add_binder',
    tab_title='Add Binder',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddBinderView(FormView):
    title = 'Add Binder'
    schema = BinderSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct.pop('name')
        binder = registry.content.create('Binder', **appstruct)
        binder.__creator__ = oid_of(self.request.user)
        self.context[name] = binder
        return HTTPFound(self.request.mgmt_path(self.context, '@@contents'))

@view_config(context=IFolder, name='createsomething')
def createsomething(context, request):
    def randchar(extra=''):
        return random.choice(
            string.ascii_uppercase + string.digits + extra
            )
    def randchar_with_space():
        return randchar(' ')
    for i in range(100):
        name = ''.join([randchar() for x in range(7)])
        value = ''.join([randchar_with_space() for x in range(1000)])
        doc = request.registry.content.create('Document', name, value)
        context.add(name, doc)
    return Response('OK')

@view_config(name='btest')
def btest(context, request):
    from substanced.audit import AuditScribe
    t = time.time()
    auditscribe = AuditScribe(context)
    auditscribe.add('foo', None, a=t)
    response = request.response
    response.body = 'OK'
    response.content_type = 'text/plain'
    return response

@view_config(name='ctest')
def ctest(context, request):
    demo_catalog = find_catalog(context, 'sdidemo')
    system_catalog = find_catalog(context, 'system')
    q = ( demo_catalog['title'].eq('fred') &
          system_catalog['content_type'].eq('Document') )
    resultset = q.execute().all()
    request.response.content_type = 'text/plain'
    request.response.body = str(list(resultset))
    return request.response
    
    
    
