"""Export advocate europe proposal comments.

This is registered as console script 'export_comments'
in setup.py.
"""

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
from adhocracy_core.interfaces import search_query

from pyramid.traversal import resource_path
from pyramid.traversal import get_current_registry

from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.comment import IComment
from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_mercator.resources.mercator2 import IMercatorProposal


def export_comments():
    """
    Export all comments from database and write them to csv file.

    --limited restricts the export to a few fields.
    """
    doc = textwrap.dedent(inspect.getdoc(export_comments))
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


def _export_comments(root, registry):
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
          partial(_get_proposal_url, registry)),
         ('Title',
          partial(_get_sheet_field, ITitle, 'title')),
         ('Comments',
          partial(_get_comments))]

    wr.writerow([name for (name, _) in fields])

    for proposal in proposals:

        result = []
        append_field = partial(_append_field, result)

        for name, get_field in fields:
            append_field(get_field(proposal))

        wr.writerow(result)

    print('Exported mercator comments to %s' % filename)


def _normalize_text(s: str) -> str:
    """Normalize text to put it in CVS."""
    return s.replace(';', '')


def _append_field(result, content):
    result.append(_normalize_text(content))


def _get_proposal_url(registry: Registry,
                      proposal: IMercatorProposal) -> str:
    path = resource_path(proposal)
    frontend_url = registry.settings.get('adhocracy.frontend_url')
    return frontend_url + '/r' + path


def _get_sheet_field(sheet, field, resource):
    registry = get_current_registry(resource)
    return registry.content.get_sheet_field(resource, sheet, field)


def _get_comments(proposal):
    item = find_interface(proposal, IItem)
    catalogs = find_service(proposal, 'catalogs')
    query = search_query._replace(root=item,
                                  interfaces=ICommentVersion,
                                  indexes={'tag': 'LAST'},
                                  sort_by='item_creation_date',
                                  )
    result = catalogs.search(query)
    comments = list(result.elements)
    comment_content = [_get_sheet_field(IComment, 'content', comment)
                       for comment in comments]
    comment_content_flat = '\n----------\n'.join(comment_content)
    return comment_content_flat
