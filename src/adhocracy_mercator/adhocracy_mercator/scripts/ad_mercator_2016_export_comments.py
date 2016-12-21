"""Script to export advocate europe proposal comments."""

import argparse
import csv
import inspect
import textwrap
from functools import partial

from pyramid.registry import Registry
from pyramid.paster import bootstrap
from pyramid.traversal import find_interface
from substanced.util import find_service
from adhocracy_core.utils import create_filename

from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import search_query

from pyramid.traversal import resource_path

from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.comment import IComment
from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_core.scripts import append_cvs_field
from adhocracy_core.scripts import get_sheet_field_for_partial
from adhocracy_mercator.resources.mercator2 import IMercatorProposal


def main():
    """Export all comments from database and write them to csv file."""
    doc = textwrap.dedent(inspect.getdoc(main))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('config')
    parser.add_argument('-l',
                        '--limited',
                        help='only export a limited subset of all fields',
                        action='store_true')
    args = parser.parse_args()
    env = bootstrap(args.config)
    root = env['root']
    registry = env['registry']
    _export_comments(root, registry)
    env['closer']()


def _export_comments(root: IResource, registry: Registry):
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=IMercatorProposal,
                                  resolve=True,
                                  )
    proposals = catalogs.search(query).elements

    filename = create_filename(directory='./var/export',
                               prefix='ae-2016-comments',
                               suffix='.csv')
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)

    fields = \
        [('URL',
          partial(_get_url, registry)),
         ('Title',
          partial(get_sheet_field_for_partial, ITitle, 'title')),
         ('Comments',
          partial(_get_comments, registry))]

    wr.writerow([name for (name, _) in fields])

    for proposal in proposals:

        result = []
        append_field = partial(append_cvs_field, result)

        for name, get_field in fields:
            append_field(get_field(proposal))

        wr.writerow(result)

    print('Exported mercator comments to %s' % filename)


def _get_url(registry: Registry, context: IResource) -> str:
    path = resource_path(context)
    frontend_url = registry.settings.get('adhocracy.canonical_url')
    return frontend_url + '/r' + path


def _get_comments(registry: Registry, proposal: IMercatorProposal):
    item = find_interface(proposal, IItem)
    catalogs = find_service(proposal, 'catalogs')
    query = search_query._replace(root=item,
                                  interfaces=ICommentVersion,
                                  indexes={'tag': 'LAST'},
                                  sort_by='item_creation_date',
                                  )
    result = catalogs.search(query)
    comments = list(result.elements)
    comment_content = [registry.context.get_sheet_field(comment, IComment,
                                                        'content')
                       for comment in comments]
    comment_content_flat = '\n----------\n'.join(comment_content)
    return comment_content_flat
