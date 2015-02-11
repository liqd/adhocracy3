#!/usr/bin/env python
"""Merge keys from stdin into translation files.

Does remove existing entries for keys that are not in stdin.
"""

import fileinput
import json


FILES = [
    'src/adhocracy_frontend/adhocracy_frontend/static/i18n/de.json',
    'src/adhocracy_frontend/adhocracy_frontend/static/i18n/en.json',
]


if __name__ == '__main__':
    keys = [l.rstrip() for l in fileinput.input()]

    for filename in FILES:
        with open(filename) as fh:
            data = json.load(fh)

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
