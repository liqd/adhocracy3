import time
from pyramid.view import (
    view_config,
    view_defaults,
)
from pyramid.decorator import reify
from pyramid.security import has_permission
from pyramid.traversal import resource_path

from cornice.errors import Errors
from cornice.schemas import (
    validate_colander_schema,
    CorniceSchema,
)
from cornice.util import json_error
from substanced.interfaces import (
    IPropertySheet,
    IFolder,
)
from substanced.folder import FolderKeyError
from substanced.interfaces import IAutoNamingFolder
from substanced.util import get_oid

from adhocracy.contents.interfaces import (
    IContent,
    INode,
    )
from adhocracy.rest.views.interfaces import (
    ContentGETSchema,
    ContentPOSTSchema,
    ContentPUTSchema,
    )


# TODO make decorator to run multiple request data validators
# TODO validate addable types for post requests
# TODO validate allowed interfaces to get/set data
def validate_request_data(schema, request):
        """Validate request POST/GET data with colander schema.
           Add errors to request.errors
           Add validated data to request.validated
           Raises HTTError 400 if request.errors is not empty
        """
        schema = CorniceSchema(schema)
        validate_colander_schema(schema, request)
        if request.errors:
            raise json_error(request.errors)


@view_defaults(
    renderer = 'jsoncolander',
    context = IContent
)
class ContentView():
    """Default views for adhocracy content.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.registry = request.registry
        # add cornice errors object to request
        self.request.errors = Errors()
        # add dictionary to store validated reqeuest data
        self.request.validated = {}
        # set reserved names for folder children
        self.reserved_names = ("_local", "_versions", "_tags")

    @reify
    def sheets(self):
        """Returns dictwith interface-name as keys and property sheet as
           values.
        """
        sheets = list(self.registry.getAdapters((self.context, self.request),
                                                IPropertySheet,))
        sheets.sort()
        return dict(sheets)

    @reify
    def viewable_sheets(self):
        sheets = {}
        for ifacename, sheet in self.sheets.items():
            permission = sheet.view_permission
            if has_permission(permission, self.context, self.request):
                sheets[ifacename] = sheet
        return sheets

    @reify
    def editable_sheets(self):
        sheets = {}
        for ifacename, sheet in self.sheets.items():
            permission = sheet.edit_permission
            if has_permission(permission, self.context, self.request):
                sheets[ifacename] = sheet
        return sheets

    @reify
    def addable_content_types(self):
        addables = self.registry.content.addable_content_types(self.context)
        return addables

    def set_path_content_type(self, data):
        data["path"] = resource_path(self.context).split(".")[-1]
        data["content_type"] = self.request.registry.content.typeof(self.context)

    @view_config(request_method='GET')
    def get(self):
        data = ContentGETSchema().serialize()
        self.set_path_content_type(data)
        for ifacename, sheet in self.viewable_sheets.items():
            cstruct = sheet.cstruct()
            data["data"][ifacename] = cstruct
        return data

    @view_config(request_method='HEAD')
    def head(self):
        return self.meta()

    @view_config(request_method='OPTIONS')
    def options(self):
        data = {}
        if self.addable_content_types:
            data["POST"] = self.addable_content_types
        if self.editable_sheets:
            data["PUT"] = [x for x in self.editable_sheets]
        if self.viewable_sheets:
            data["GET"] = [x for x in self.viewable_sheets]
        if True: # FIXME: how do we want head to behave?
            data["HEAD"] = []
        return data

    @view_config(request_method='POST')
    def post(self):
        #validate request data
        validate_request_data(ContentPOSTSchema, self.request)
        data = self.request.validated
        #create content
        content = self.registry.content.create(data["content_type"])
        #set content data
        for ifacename in data["data"]:
            sheet = self.registry.getMultiAdapter((content, self.request),\
                                                  IPropertySheet, ifacename)
            sheet.set(data["data"][ifacename])
        #add content to parent
        name = getattr(content, "name", "")
        try:
            self.context.check_name(name, reserved_names=self.reserved_names)
        except (FolderKeyError, ValueError):
            name += str(time.time())
        self.context.add(name, content)
        return {
            "path": resource_path(content),
            "content_type": self.request.registry.content.typeof(content)
            }

    @view_config(request_method='PUT')
    def put(self):
        #validate request data
        validate_request_data(ContentPUTSchema, self.request)
        data = self.request.validated
        #set content data
        content = self.context
        for ifacename in data["data"]:
            sheet = self.registry.getMultiAdapter((content, self.request), IPropertySheet, ifacename)
            sheet.set(data["data"][ifacename])
        return {
            "path": resource_path(content),
            "content_type": self.request.registry.content.typeof(self.context)
            }


@view_defaults(
    renderer = 'jsoncolander',
    context = INode
)
class NodeView(ContentView):
    """Default views for supergraph nodes.
    """

    @view_config(request_method='GET')
    def get(self):
        return super(NodeView, self).get()

    @view_config(request_method='HEAD')
    def head(self):
        return super(NodeView, self).head()

    @view_config(request_method='OPTIONS')
    def options(self):
        return super(NodeView, self).options()

    @view_config(request_method='PUT')
    def put(self):
        #validate request data
        # TODO validate and require correct IVersionable data
        validate_request_data(ContentPUTSchema, self.request)
        data = self.request.validated
        #create new node content
        content = self.registry.content.create(data["content_type"])
        #set content data
        for ifacename in data["data"]:
            sheet = self.registry.getMultiAdapter((content, self.request), IPropertySheet, ifacename)
            sheet.set(data["data"][ifacename])
        #add new node content to parent
        parent = self.context.__parent__
        if IAutoNamingFolder.providedBy(parent):
            parent.add_next(content)
        else:
            parent.add(str(time.time()), content)
        return {"path": resource_path(content)}



