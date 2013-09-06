from substanced.sdi import sdi_add_views
from substanced.sdi.views.folder import (
    FolderContents,
    folder_contents_views,
)


@folder_contents_views()
class AdhocracyFolderContents(FolderContents):
    """Subtyped to customize sdi_add_views
    """

    def sdi_add_views(self, context, request):
        add_views = sdi_add_views(context, request)
        #TODO Hack
        if "adhocracy" in request.registry.content.typeof(context):
            addables = request.registry.content.addable_content_types(context)
            add_views = [x for x in add_views if x['content_type'] in addables]
        return add_views



