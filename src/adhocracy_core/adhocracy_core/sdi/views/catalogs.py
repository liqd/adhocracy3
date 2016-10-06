"""Catalogs tab."""
from hypatia.interfaces import IIndex
from pyramid.interfaces import IRequest
from substanced.interfaces import ICatalog
from substanced.interfaces import IRoot
from substanced.folder.views import folder_contents_views
from substanced.sdi import RIGHT
from substanced.util import _
from adhocracy_core.catalog import ICatalogsService
from adhocracy_core.sdi.views.contents import AdhocracyFolderContents


def is_catalogish(context: object, request: IRequest) -> bool:
    """Return true if context is catalog or root."""
    if IRoot.providedBy(context):
        return True
    elif ICatalogsService.providedBy(context):
        return True
    elif ICatalog.providedBy(context):
        return True
    else:
        return False


@folder_contents_views(view_permission='sdi.manage-catalog',
                       name='catalogs',
                       tab_title=_('Catalogs'),
                       tab_near=RIGHT,
                       tab_condition=is_catalogish,
                       )
class AdhocracyFolderServices(AdhocracyFolderContents):

    def get_default_query(self):
        """The default query function for a folder."""
        system_catalog = self.system_catalog
        folder = self.context
        path = system_catalog['path']
        interfaces = system_catalog['interfaces']
        allowed = system_catalog['allowed']
        q = (path.eq(folder, depth=1, include_origin=False) &
             interfaces.any([ICatalogsService, ICatalog, IIndex]) &
             allowed.allows(self.request, 'sdi.view')
             )
        return q

    get_query = get_default_query
