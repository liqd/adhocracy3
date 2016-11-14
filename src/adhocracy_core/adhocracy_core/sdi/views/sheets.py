"""Sheets tab and add view for resources."""
from collections import OrderedDict

from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRequest
from substanced.sdi import mgmt_view
from substanced.util import _
from substanced.sdi import LEFT

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IResourceSheet
from adhocracy_core.schema import MappingSchema
from adhocracy_core.sdi.form import FormView
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import create_schema


def has_editable_sheets(context: object, request: IResource) -> bool:
    """Return True if `context` has editable sheets."""
    try:
        sheets = request.registry.content.get_sheets_edit(context, request)
    except KeyError:
        return False
    return bool(sheets)


@mgmt_view(
    name='properties',
    renderer='substanced.property:templates/propertysheets.pt',
    tab_title=_('Sheets'),
    permission='sdi.manage-sheets',
    tab_near=LEFT,
    tab_condition=has_editable_sheets,
)
class EditResourceSheets(FormView):
    """Edit resource sheets form tab."""

    buttons = (_('save'),)

    def __init__(self, context: IResource, request: IRequest):
        """Setup active sheet schema."""
        super().__init__(context, request)
        self.registry = self.request.registry
        self.sheets = self._get_editable_sheets()
        self.sheet_names = list(self.sheets.keys())
        self.active_sheet_name = self._get_active_sheet_name()
        self.active_sheet = self._get_active_sheet()
        self.schema = self.active_sheet.get_schema_with_bindings()

    def _get_active_sheet_name(self) -> str:
        subpath = self.request.subpath
        if subpath:
            name = subpath[0]
        else:
            name = self.sheet_names[0]
        return name

    def _get_active_sheet(self) -> IResourceSheet:
        name = self._get_active_sheet_name()
        return self.sheets[name]

    def _get_editable_sheets(self) -> {}:
        sheets = self.registry.content.get_sheets_edit(self.context,
                                                       self.request)
        return OrderedDict([(s.meta.isheet.__identifier__.split('.')[-1],
                             s) for s in sheets])

    def save_success(self, appstruct: dict):
        self.active_sheet.set(appstruct)
        self.request.sdiapi.flash('Updated sheets', 'success')
        return HTTPFound(self.request.sdiapi.mgmt_path(
            self.context, '@@properties', self.active_sheet_name))

    def show(self, form):
        appstruct = self.active_sheet.get()
        return {'form': form.render(appstruct=appstruct,
                                    readonly=False)}


class AddResourceSheetsBase(FormView):
    """Add resource form, subclass and set content_type attribute."""

    buttons = (_('add'),)
    iresource = None
    _disabled = (IMetadata)
    """Sheets not working with this add view yet, use sheets tabs instead."""

    def __init__(self, context: IResource, request: IRequest):
        """Setup active sheet schema."""
        super().__init__(context, request)
        self.registry = self.request.registry
        self.sheets = self._get_creatable_sheets()
        self.schema = self._get_schema_with_bindings()
        self.meta = self.registry.content.resources_meta[self.iresource]
        content_name = self.meta.content_name or self.iresource.__identifier__
        self.title = _('Add {0}'.format(content_name))

    def _get_creatable_sheets(self) -> {}:
        sheets = self.registry.content.get_sheets_create(
            self.context,
            self.request,
            iresource=self.iresource)
        sheets = [x for x in sheets if x.meta.isheet not in self._disabled]
        return OrderedDict([(s.meta.isheet.__identifier__, s) for s in sheets])

    def _get_schema_with_bindings(self) -> MappingSchema:
        schema = create_schema(MappingSchema, self.context, self.request,
                               creating=True)
        for name, sheet in self.sheets.items():
            sheet_schema = sheet.get_schema_with_bindings()
            schema.add(sheet_schema)
        return schema

    def add_success(self, appstructs):
        self.registry.content.create(self.iresource.__identifier__,
                                     parent=self.context,
                                     appstructs=appstructs,
                                     request=self.request,
                                     registry=self.registry,
                                     )
        return HTTPFound(location=self.request.sdiapi.mgmt_path(self.context))
