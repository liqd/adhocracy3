"""Delete not referenced images.

This is registered as console script.
"""
from datetime import timedelta
import transaction
import argparse
import inspect
import logging

from pyramid.paster import bootstrap
from substanced.util import find_service

from adhocracy_core.interfaces import Reference
from adhocracy_core.interfaces import search_query
from adhocracy_core.interfaces import FieldComparator
from adhocracy_core.resources.image import IImage
from adhocracy_core.sheets.image import IImageReference
from adhocracy_core.utils import now


logger = logging.getLogger(__name__)


def delete_not_referenced_images():  # pragma: no cover
    """Delete images older than `max_age` that are not referenced.

    usage::

        bin/delete_not_referenced_images etc/development.ini  --max_age 10
    """
    docstring = inspect.getdoc(delete_not_referenced_images)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('-m',
                        '--max_age',
                        help='Max age in days of images',
                        default=30,
                        type=int)
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    _delete_not_referenced_images(env['root'],
                                  args.max_age,
                                  )
    transaction.commit()
    env['closer']()


def _delete_not_referenced_images(root,
                                  max_age: int,
                                  ):
    catalogs = find_service(root, 'catalogs')
    max_date = now() - timedelta(days=max_age)
    query = search_query._replace(interfaces=IImage,
                                  resolve=True,
                                  indexes={'item_creation_date':
                                           (FieldComparator.lt.value, max_date)
                                           }
                                  )
    images = catalogs.search(query).elements
    msg = 'Found {0} images older then {1} days'.format(len(images), max_age)
    logger.info(msg)
    for image in images:
        picture_reference = Reference(None, IImageReference, '', image)
        query = search_query._replace(references=(picture_reference,))
        referencing = catalogs.search(query)
        if referencing.count > 0:
            msg = 'Deleting image {0} that is not referenced'.format(image)
            logger.info(msg)
            del image.__parent__[image.__name__]
