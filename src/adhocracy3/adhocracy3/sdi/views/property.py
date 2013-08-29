from pyramid.security import (
    has_permission,
    )
from pyramid.httpexceptions import (
    HTTPNotFound,
    )
from substanced.property import IPropertySheet
from substanced.sdi.views.property import PropertySheetsView
from substanced.sdi import mgmt_view



def has_permission_to_view_any_propertysheet(context, request):

    adapters = request.registry.getAdapters((context, request), IPropertySheet,)
    sheets = [sheet for name, sheet in adapters]

    for sheet in sheets:
        permissions = getattr(sheet, 'permissions', None)
        if not permissions:
            return True
        view_permission = dict(permissions).get('view')
        if view_permission:
            if has_permission(view_permission, context, request):
                return True
        else:
            return True
    return False


@mgmt_view(
    propertied=False,
    name='properties',
    renderer='substanced.sdi.views:templates/propertysheets.pt',
    tab_title='Properties',
    tab_condition=has_permission_to_view_any_propertysheet,
    permission='sdi.view',
    )
class PropertySheetsAdhocracyView(PropertySheetsView):
    """Subclassed to make the content type property sheet look up
       work.
       We dont use the global config to store property sheet factories.
       Instead we look up adapters.
    """

    def __init__(self, request):
        self.request = request
        self.context = request.context
        viewable_sheets = self.viewable_sheets()
        if not viewable_sheets:
            raise HTTPNotFound('No viewable property sheets')
        subpath = request.subpath
        active_sheet = None
        if subpath:
            active_sheet_name = subpath[0]
            active_sheet = dict(viewable_sheets).get(
                active_sheet_name)
        if not active_sheet:
            active_sheet_name, active_sheet = viewable_sheets[0]
        self.active_sheet = self.active_factory = active_sheet
        self.active_sheet_name = active_sheet_name
        self.sheet_names = [x[0] for x in viewable_sheets]
        self.schema = self.active_sheet.schema

    def viewable_sheets(self):
        adapters = self.request.registry.getAdapters((self.context, self.request), IPropertySheet,)
        candidates = [(name, sheet) for name, sheet in adapters]
        L = []
        for name, sheet in candidates:
            if not self.has_permission_to('view', sheet):
                continue
            L.append((name, sheet))
        return L
