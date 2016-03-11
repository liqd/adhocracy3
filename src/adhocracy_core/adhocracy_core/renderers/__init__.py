"""Additional pyramid renderers."""
import pkg_resources
from yaml import safe_load


class YAMLToPython:
    """YAML to python renderer using :func:`yaml.safe_load`."""

    def __init__(self, info: dict):
        """See :method:`pyramid.interfaces.IRendererFactory.__call__`."""

    def __call__(self, value: dict, system: dict) -> object:
        """Render yaml file :term:asset` given in `system` to python.

        :param value: additional keyword passed to the renderer, not used.
        :param system: dict including `renderer_name` (yaml file asset)
        :raise ValueError: if the yaml file asset does not exist.

        See :method:`pyramid.interfaces.IRenderer.__call__`
        """
        asset = system['renderer_name']
        package, filename = asset.split(':')
        path = pkg_resources.resource_filename(package, filename)
        if not pkg_resources.resource_exists(package, filename):
            msg = 'Missing template asset: {0}:{1}'
            raise ValueError(msg.format(package, filename))
        with open(path, 'r') as f:
            appstruct = safe_load(f)
        return appstruct


def includeme(config):
    """Register renderers."""
    config.add_renderer(name='.yaml', factory=YAMLToPython)
