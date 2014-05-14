"""Rest API configuration."""
import logging


logger = logging.getLogger(__name__)


def includeme(config):  # pragma: no cover
    """Run pyramid configuration."""
    config.include('cornice')
    config.scan('.views')
    config.scan('.exceptions')
