"""Base views."""
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden

from substanced.sdi import mgmt_view
from substanced.sdi import sdi_mgmt_views


class ManagementViews(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @mgmt_view(tab_condition=False,
               permission=NO_PERMISSION_REQUIRED,
               )
    @mgmt_view(name='manage_main',
               tab_condition=False,
               permission=NO_PERMISSION_REQUIRED,
               )
    def manage_main(self):
        sdi_tabs = sdi_mgmt_views(self.context, self.request)
        can_use_sdi = self.request.has_permission('sdi.view', self.context)
        if sdi_tabs and can_use_sdi:
            view_name = '@@%s' % (sdi_tabs[0]['view_name'],)
            location = self.request.sdiapi.mgmt_path(self.request.context,
                                                     view_name)
            return HTTPFound(location=location)
        else:
            self.request.session['came_from'] = self.request.url
            location = self.request.sdiapi.mgmt_path(self.request.virtual_root,
                                                     '@@login')
            raise HTTPForbidden(location=location)
