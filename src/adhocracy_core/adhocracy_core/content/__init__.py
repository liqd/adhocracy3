"""Create resources, get sheets/metadata, permission checks."""
from copy import copy

from pyramid.request import Request
from pyramid.util import DottedNameResolver
from pyramid.decorator import reify
from pyramid.traversal import resource_path
from substanced.content import ContentRegistry
from substanced.content import add_content_type
from substanced.content import add_service_type
from substanced.workflow import IWorkflow
from zope.interface.interfaces import IInterface

from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import ResourceMetadata
from adhocracy_core.utils import get_iresource


resolver = DottedNameResolver()


class ResourceContentRegistry(ContentRegistry):

    """Extend substanced content registry to work with resources."""

    def __init__(self, registry):
        super().__init__(registry)
        self.resources_meta = {}
        """Resources meta mapping.

        Dictionary with key iresource (`resource type` interface) and value
        :class:`adhocracy_core.interfaces.ResourceMetadata`.
        """
        self.sheets_meta = {}
        """Sheets meta mapping.

        Dictionary with key isheet (`sheet type` interface) and value
        :class:`adhocracy_core.interfaces.SheetMetadata`.
        """
        self.workflows_meta = {}
        """Dictionary with key workflow name and value data.

        The value data structure is defined in
        :class:`adhocracy_core.workflows.schemas.Workflow`
        """
        self.workflows = {}
        """Dictionary with key workflow name and value
        :class:`substanced.workflow.IWorkflow`.
        """

    def get_resources_meta_addable(self, context: object,
                                   request: Request) -> list:
        """Get addable resource meta for context, mind permissions."""
        iresource = get_iresource(context)
        addables = self.resources_meta_addable[iresource]
        addables_allowed = []
        for resource_meta in addables:
            permission = resource_meta.permission_create
            ignore_permission = self._only_first_version_exists(context,
                                                                resource_meta)
            if ignore_permission:
                # FIXME this is a work around to allow the bplan workfow
                # to disable edit permission but allow create permision for
                # proposals. This might cause security issues if you don't
                # create the version 0 and 1 in one batch request!
                addables_allowed.append(resource_meta)
            elif request.has_permission(permission, context):
                addables_allowed.append(resource_meta)
        return addables_allowed

    def _only_first_version_exists(self, context: object,
                                   meta: ResourceMetadata) -> bool:
        only_first_version = False
        is_item_version = meta.iresource.isOrExtends(IItemVersion)
        has_item_parent = IItem.providedBy(context)
        if has_item_parent and is_item_version:
            children = context.values()
            versions = [x for x in children if IItemVersion.providedBy(x)]
            only_first_version = len(versions) == 1
        return only_first_version

    @reify
    def resources_meta_addable(self):
        """Addable resources metadata mapping.

        Dictionary with key iresource (`resource type` interface)` and value
        list of :class:`adhocracy_core.interfaces.ResourceMetadata`.
        The value includes only addables for a context with `resource type`.
        """
        resources_addables = {}
        for iresource, resource_meta in self.resources_meta.items():
            addables = resource_meta.element_types
            all_addables = []
            for iresource_, resource_meta_ in self.resources_meta.items():
                is_implicit = resource_meta_.is_implicit_addable
                for iresource_addable in addables:
                    is_subtype = is_implicit\
                        and iresource_.extends(iresource_addable)
                    is_is = iresource_ is iresource_addable
                    if is_subtype or is_is:
                        all_addables.append(resource_meta_)
            resources_addables[iresource] = all_addables
        return resources_addables

    @property
    def permissions(self) -> [str]:
        """Set of all permissions defined in the system."""
        perms = self._builtin_permissions
        for resource_meta in self.resources_meta.values():
            perms.update(self._get_resource_permissions(resource_meta))
        for sheet_meta in self.sheets_meta.values():
            perms.update(self._get_sheet_permissions(sheet_meta, perms))
        for workflow_meta in self.workflows_meta.values():
            perms.update(self._get_workflow_permissions(workflow_meta))
        perms.update(self._get_views_permissions())
        return perms

    @property
    def _builtin_permissions(self):
        return {'hide', 'edit_group', 'do_transition'}

    def _get_resource_permissions(self, resource_meta):
        return [p for p in [resource_meta.permission_create,
                            resource_meta.permission_view]
                if p != '']

    def _get_sheet_permissions(self, sheet_meta, perms):
        return [p for p in [sheet_meta.permission_view,
                            sheet_meta.permission_edit,
                            sheet_meta.permission_create]
                if p != '']

    def _get_views_permissions(self):
        permissions = self.registry.introspector.get_category('permissions')
        if permissions is None:
            return []
        return [v['introspectable'].title for v in permissions]

    def _get_workflow_permissions(self, workflow_meta):
        return [t['permission'] for t in workflow_meta['transitions'].values()]

    def get_sheet(self, context: object, isheet: IInterface) -> ISheet:
        """Get sheet for `context` and set the 'context' attribute.

        :raise adhocracy_core.exceptions.RuntimeConfigurationError:
           if there is no `isheet` sheet registered for context.
        """
        if not isheet.providedBy(context):
            msg = 'Sheet {0} is not provided by resource {1}'\
                .format(isheet.__identifier__, resource_path(context))
            raise RuntimeConfigurationError(msg)
        meta = self.sheets_meta[isheet]
        sheet = meta.sheet_class(meta, context, self.registry)
        return sheet

    def get_sheets_all(self, context: object) -> list:
        """Get all sheets for `context` and set the 'context' attribute."""
        iresource = get_iresource(context)
        sheets = self.sheets_all[iresource].copy()
        self._add_context(sheets, context)
        return sheets

    def get_sheets_create(self, context: object, request: Request=None,
                          iresource: IInterface=None):
        """Get creatable sheets for `context` and set the 'context' attribute.

        :param iresource: If set return creatable sheets for this resource
                         type. Else return the creatable sheets of `context`.
        :param request: If set check permissions.
        """
        iresource = iresource or get_iresource(context)
        sheets = self.sheets_create[iresource].copy()
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_create', context, request)
        return sheets

    def get_sheets_edit(self, context: object, request: Request=None) -> list:
        """Get editable sheets for `context` and set the 'context' attribute.

        :param request: If set check permissions.
        """
        iresource = get_iresource(context)
        sheets = self.sheets_edit[iresource].copy()
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_edit', context, request)
        return sheets

    def get_sheets_read(self, context: object, request: Request=None) -> list:
        """Get readable sheets for `context` and set the 'context' attribute.

        :param request: If set check permissions.
        """
        iresource = get_iresource(context)
        sheets = self.sheets_read[iresource].copy()
        self._add_context(sheets, context)
        self._filter_permission(sheets, 'permission_view', context, request)
        return sheets

    @staticmethod
    def _add_context(sheets: list, context: object):
        for sheet in sheets:
            sheet.context = context

    @staticmethod
    def _filter_permission(sheets: list, permission_attr: str, context: object,
                           request: Request=None):
        if request is None:
            return
        sheets_candiates = copy(sheets)
        for sheet in sheets_candiates:
            permission = getattr(sheet.meta, permission_attr)
            if not request.has_permission(permission, context):
                sheets.remove(sheet)

    @reify
    def sheets_all(self) -> dict:
        """Sheet mapping.

        Dictionary with key iresource (`resource type` interface) and
        value list of sheets.
        Mind to set the `context` attribute before set/get sheet data.
        """
        resource_sheets_all = {}
        registry = self.registry
        for resource_meta in self.resources_meta.values():
            isheets = set(resource_meta.basic_sheets +
                          resource_meta.extended_sheets)
            sheets = []
            for isheet in isheets:
                sheet_meta = self.sheets_meta[isheet]
                context = None
                sheet = sheet_meta.sheet_class(sheet_meta, context, registry)
                sheets.append(sheet)
            resource_sheets_all[resource_meta.iresource] = sheets
        return resource_sheets_all

    @reify
    def sheets_create(self) -> dict:
        """Createable sheets mapping.

        Dictionary with key `resource type` and value list of creatable sheets.
        """
        return self._filter_sheets_all_by_attribute('creatable')

    @reify
    def sheets_create_mandatory(self) -> dict:
        """CreateMandatory sheets mapping.

        Dictionary with key `resource type` and value list of
        create mandatory sheets.
        """
        return self._filter_sheets_all_by_attribute('create_mandatory')

    @reify
    def sheets_edit(self) -> dict:
        """Editable sheets mapping.

        Dictionary with key `resource type` and value list of
        editable sheets.
        """
        return self._filter_sheets_all_by_attribute('editable')

    @reify
    def sheets_read(self) -> dict:
        """Readable sheets mapping.

        Dictionary with key `resource type` and value list of
        readable sheets.
        """
        return self._filter_sheets_all_by_attribute('readable')

    def _filter_sheets_all_by_attribute(self, attribute: str) -> list:
        sheets_all_filtered = {}
        for iresource, sheets in self.sheets_all.items():
            filtered = filter(lambda s: getattr(s.meta, attribute), sheets)
            sheets_all_filtered[iresource] = [x for x in filtered]
        return sheets_all_filtered

    def resolve_isheet_field_from_dotted_string(self, dotted: str) -> tuple:
        """Resolve `dotted` string to isheet and field name and schema node.

        :dotted: isheet.__identifier__ and field_name separated by ':'
        :return: tuple with isheet (ISheet), field_name (str), field schema
                 node (colander.SchemaNode).
        :raise ValueError: If the string is not dotted or it cannot be
            resolved to isheet and field name.
        """
        if ':' not in dotted:
            raise ValueError(
                'Not a colon-separated dotted string: {}'.format(dotted))
        name = ''.join(dotted.split(':')[:-1])
        field = dotted.split(':')[-1]
        try:
            isheet = resolver.resolve(name)
        except ImportError:
            raise ValueError('No such sheet: {}'.format(name))
        if not (IInterface.providedBy(isheet) and isheet.isOrExtends(ISheet)):
            raise ValueError('Not a sheet: {}'.format(name))
        schema = self.sheets_meta[isheet].schema_class()
        node = schema.get(field, None)
        if not node:
            raise ValueError('No such field: {}'.format(dotted))
        return isheet, field, node

    def get_workflow(self, name: str) -> IWorkflow:
        """Get workflow with name `name`.

        :raises RuntimeConfigurationError: if workflow is not registered
        """
        try:
            workflow = self.workflows[name]
        except KeyError:
            msg = 'Workflow is not registered: {0}'.format(name)
            raise RuntimeConfigurationError(msg)
        return workflow


def includeme(config):  # pragma: no cover
    """Add content registry, register substanced content_type decorators."""
    config.registry.content = ResourceContentRegistry(config.registry)
    config.add_directive('add_content_type', add_content_type)
    config.add_directive('add_service_type', add_service_type)
