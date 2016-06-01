"""Contents tab."""
from substanced.folder.views import FolderContents
from substanced.folder.views import folder_contents_views


@folder_contents_views()
class AdhocracyFolderContents(FolderContents):
    """Default contents tab."""

    def sdi_addable_content(self) -> [dict]:
        registry = self.request.registry
        metas = registry.content.get_resources_meta_addable(self.context,
                                                            self.request)
        addables = [m.iresource.__identifier__ for m in metas
                    if m.is_sdi_addable]
        introspector = registry.introspector
        cts = []
        for data in introspector.get_category('substance d content types'):
            intr = data['introspectable']
            if intr['content_type'] in addables:
                cts.append(data)
        return cts
