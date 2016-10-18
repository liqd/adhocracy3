"""Contents tab."""
from substanced.folder.views import FolderContents
from substanced.folder.views import folder_contents_views
from substanced.sdi import LEFT
from adhocracy_core.interfaces import IResource


@folder_contents_views(view_permission='sdi.view-contents',
                       tab_near=LEFT)
class AdhocracyFolderContents(FolderContents):
    """Default contents tab."""

    def sdi_addable_content(self) -> [dict]:
        registry = self.request.registry
        try:
            metas = registry.content.get_resources_meta_addable(self.context,
                                                                self.request)
        except KeyError:  # happens if context has no iresoure interface
            return []
        addables = [m.iresource.__identifier__ for m in metas
                    if m.is_sdi_addable]
        introspector = registry.introspector
        cts = []
        for data in introspector.get_category('substance d content types'):
            intr = data['introspectable']
            if intr['content_type'] in addables:
                cts.append(data)
        return cts

    def get_query(self):
        """The default query function for a folder."""
        system_catalog = self.system_catalog
        folder = self.context
        path = system_catalog['path']
        interfaces = system_catalog['interfaces']
        allowed = system_catalog['allowed']
        q = (path.eq(folder, depth=1, include_origin=False) &
             interfaces.any([IResource]) &
             allowed.allows(self.request, 'sdi.view')
             )
        return q
