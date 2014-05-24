"""Resource type configuration and default factory."""
import datetime

from pyramid.path import DottedNameResolver
from pyramid.threadlocal import get_current_registry
from pyramid.config import Configurator
from substanced.content import add_content_type
from zope.interface import directlyProvides
from zope.interface import alsoProvides

from adhocracy.interfaces import ResourceMetadata
from adhocracy.sheets.name import IName
from adhocracy.utils import get_sheet


def add_resource_type_to_registry(metadata: ResourceMetadata,
                                  config: Configurator):
    """Add the `resource` type specified in metadata to the content registry.

    As generic factory the :class:`ResourceFactory` is used.

    """
    assert hasattr(config.registry, 'content')
    iresource = metadata.iresource
    name = metadata.content_name or iresource.__identifier__
    meta = {'content_name': name,
            'resource_metadata': metadata}
    add_content_type(config, iresource.__identifier__,
                     ResourceFactory(metadata),
                     factory_type=iresource.__identifier__, **meta)


class ResourceFactory:

    """Basic resource factory."""

    name_identifier = IName.__identifier__

    def __init__(self, metadata: ResourceMetadata):
        self.meta = metadata

    def _add(self, parent, resource, appstructs):
        """Add resource to context folder.

        Returns:
            name (String)
        Raises:
            substanced.folder.FolderKeyError
            ValueError

        """
        # TODO use seperated factory for IVersionables
        name = ''
        if self.name_identifier in appstructs:
            name = appstructs[self.name_identifier]['name']
            name = parent.check_name(name)
            appstructs[self.name_identifier]['name'] = name
        if not name:
            name = datetime.datetime.now().isoformat()
        if self.meta.use_autonaming:
            prefix = self.meta.autonaming_prefix
            name = parent.next_name(resource, prefix=prefix)
        parent.add(name, resource, send_events=False)

    def __call__(self,
                 parent=None,
                 appstructs={},
                 run_after_creation=True,
                 **kwargs
                 ):
        """Triggered whan a ResourceFactory instance is called.

        Args:
            parent (IPool or None): Add the new resource to this pool.
                                    None value is allowed to create non
                                    persistent Resources (without OID/parent).
            appstructs (dict): Key/Values of sheet appstruct data.
                               Key is anidentifier of a sheet interface.
                               Value is the data to set.
            after_creation (bool): Whether to invoke after_creation hooks,
                                   Default is True.
                                   If parent is None you should set this False
            **kwargs: Arbitary keyword arguments. Will be passed along to
                after_creation hooks as 3rd argument 'options'.

        Returns:
            object (IResource): the newly created resource

        """
        resource = self.meta.content_class()
        directlyProvides(resource, self.meta.iresource)
        isheets = self.meta.basic_sheets + self.meta.extended_sheets
        alsoProvides(resource, isheets)

        if parent is not None:
            self._add(parent, resource, appstructs)
        else:
            resource.__parent__ = None
            resource.__name__ = ''

        if appstructs:
            for key, struct in appstructs.items():
                isheet = DottedNameResolver().maybe_resolve(key)
                sheet = get_sheet(resource, isheet)
                if sheet.meta.readonly:
                    continue
                else:
                    sheet.set(struct)

        if run_after_creation:
            registry = get_current_registry()
            for call in self.meta.after_creation:
                call(resource, registry, options=kwargs)

        return resource


def includeme(config):
    """Include all resource types in this package."""
    #config.include('.pool')
    #config.include('.tag')
    #config.include('.itemversion')
    #config.include('.item')
