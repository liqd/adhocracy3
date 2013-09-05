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

from adhocracy3.resources.interfaces import (
    IContent,
    )
from adhocracy3.rest.views.interfaces import (
    ContentGETSchema,
    ContentPOSTSchema,
    ContentPUTSchema,
    MetaSchema,
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
        """Returns dictwith interface-name as keys and property sheets as
           values.
        """
        sheets = self.registry.getAdapters((self.context, self.request),
                                           IPropertySheet,)
        return dict(sheets)

    @reify
    def viewable_sheets(self):
        sheets = {}
        for name, sheet in self.sheets.items():
            permission = sheet.view_permission
            if has_permission(permission, self.context, self.request):
                sheets[name] = sheet
        return sheets

    @reify
    def editable_sheets(self):
        sheets = {}
        for name, sheet in self.sheets.items():
            permission = sheet.edit_permission
            if has_permission(permission, self.context, self.request):
                sheets[name] = sheet

    @reify
    def addable_content_types(self):
        addables = self.registry.content.addable_content_types(self.context)
        return addables

    @reify
    def children(self):
        context = self.context
        return context.values() if IFolder.providedBy(context) else []

    @view_config(request_method='GET')
    def get(self):
        data = ContentGETSchema().serialize()
        # meta
        data["meta"] = self.head()
        # data
        for name, sheet in self.viewable_sheets.items():
            cstruct = sheet.cstruct()
            data["data"][name] = cstruct
        # children
        meta_children = [self.head(child) for child in self.children]
        data["children"] = meta_children
        return data

    @view_config(request_method='HEAD')
    def head(self, context=None):
        context = context or self.context
        data = MetaSchema().serialize()
        data["name"] = context.__name__
        data["path"] = resource_path(self.context)
        data["content_type"] = self.request.registry.content.typeof(context)
        data["content_type_name"] = data["content_type"]
        return data

    @view_config(request_method='OPTIONS')
    def options(self):
        data = {}
        if self.addable_content_types:
            data["POST"] = self.addable_content_types
        if self.editable_sheets:
            data["PUT"] = self.editable_sheets
        if self.viewable_sheets:
            data["GET"] = self.viewable_sheets
        return data

    @view_config(request_method='POST')
    def post(self):
        #validate request data
        validate_request_data(ContentPOSTSchema, self.request)
        data = self.request.validated
        #create content
        content = self.registry.content.create(data["content_type"],
                                               self.context)
        #set content data
        for iface in data["data"]:
            sheet = self.registry.getMultiAdapter((content, self.request), IPropertySheet, iface)
            sheet.set(data["data"][iface])
        #add content to parent
        name = getattr(content, "name", "")
        try:
            self.context.check_name(name, reserved_names=self.reserved_names)
        except FolderKeyError:
            name += str(time.time())
        self.context.add(name, content)
        return {"path:": resource_path(content)}

    @view_config(request_method='PUT')
    def put(self):
        validate_request_data(ContentPUTSchema, self.request)
        data = self.request.validated
        content = self.context
        for name in data["data"]:
            sheet = self.registry.getAdapter((content, self.reqeuest), IPropertySheet, name)
            sheet.set(data["data"][name])
        return {"path:": resource_path(content)}
