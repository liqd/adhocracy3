#!/usr/bin/env python
"""Merge keys from stdin into translation files.

Does remove existing entries for keys that are not in stdin.
"""

import json
import subprocess
import sys
import os

LOCALES = ['en', 'de']


def get_git_root():
    """Get root of git repo."""
    cmd = 'git rev-parse --show-toplevel'
    output = subprocess.check_output(cmd, shell=True)
    return output.rstrip().decode('utf8')


def get_i18n_dir(package_name):
    """Get i18n dir of a package."""
    git_root = get_git_root()
    i18n_dir = os.path.join(
        git_root, 'src', package_name, package_name, 'static', 'i18n')

    if not os.path.exists(i18n_dir):
        os.makedirs(i18n_dir)

    return i18n_dir


def get_path(package_name, file_prefix, locale):
    """Get list of translation files."""
    i18n_dir = get_i18n_dir(package_name)
    filename = '%s_%s.json' % (file_prefix, locale)
    return os.path.join(i18n_dir, filename)


def filter_core_keys(keys):
    """Exclude any keys that are already in core."""
    core_path = get_path('adhocracy_frontend', 'core', 'en')

    with open(core_path) as fh:
        data = json.load(fh)

    for key in data:
        if key in keys:
            keys.remove(key)

    return keys


if __name__ == '__main__':
    package_name = sys.argv[1]
    file_prefix = sys.argv[2]
    keys = [l.rstrip() for l in sys.stdin]

    if file_prefix != 'core':
        keys = filter_core_keys(keys)

    for locale in LOCALES:
        filename = get_path(package_name, file_prefix, locale)

        if os.path.exists(filename):
            with open(filename) as fh:
                data = json.load(fh)
        else:
            data = {}

        # add new keys
        for key in keys:
            if key not in data:
                data[key] = ''

        # remove old keys
        for key in list(data.keys()):
            if key not in keys:
                del data[key]

        with open(filename, 'w') as fh:
            json.dump(
                data,
                fh,
                indent=4,
                sort_keys=True,
                separators=(',', ': '),
                ensure_ascii=False)
