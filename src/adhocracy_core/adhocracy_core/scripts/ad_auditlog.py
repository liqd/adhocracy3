"""Script to view auditlog entries."""

import argparse
import inspect
import logging
import pprint

from datetime import datetime
from pyramid.paster import bootstrap
from substanced.interfaces import IRoot
from substanced.util import get_auditlog

from adhocracy_core.interfaces import AuditlogEntry


logger = logging.getLogger(__name__)


def main():  # pragma: no cover
    """Print auditlog entries."""
    docstring = inspect.getdoc(main)
    parser = argparse.ArgumentParser(description=docstring)
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file')
    parser.add_argument('-s',
                        '--startdate',
                        default=None,
                        help='Start of auditlog range.',
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
    parser.add_argument('-e',
                        '--enddate',
                        default=None,
                        help='End of auditlog range.',
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
    parser.add_argument('-p',
                        '--path',
                        type=str,
                        default=None,
                        help='Filter for resource path.')
    args = parser.parse_args()
    env = bootstrap(args.ini_file)
    auditlog_show(env['root'], startdate=args.startdate,
                  endtdate=args.enddate, path=args.path)
    env['closer']()


def auditlog_show(root: IRoot,
                  startdate: datetime=None,
                  endtdate: datetime=None,
                  path: str=None
                  ):
    """Show auditlog entries."""
    auditlog = get_auditlog(root)
    auditlog_entries = list(auditlog.items(min=startdate, max=endtdate))
    filtered_by_path = _filter_by_path(auditlog_entries, path)
    _print_auditlog(filtered_by_path)


def _filter_by_path(auditlog_entries: [AuditlogEntry],
                    path: str) -> [AuditlogEntry]:
    if not path:
        return auditlog_entries
    return [(t, e) for t, e in auditlog_entries
            if e.resource_path.startswith(path)]


def _print_auditlog(auditlog_entries: [AuditlogEntry]):
    pretty_printer = pprint.PrettyPrinter()
    for timestamp, auditlog_entry in auditlog_entries:
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        auditlog_entry_str = pretty_printer.pformat(auditlog_entry)
        print('{}: {}'.format(timestamp_str, auditlog_entry_str))
