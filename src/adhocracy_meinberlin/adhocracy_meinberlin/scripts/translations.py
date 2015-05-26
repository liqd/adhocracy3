"""Change the salutation in german texts.

The function change_german_salutation is registered in setup.py
in setup.py.
"""

import sys
import os
import json
import re
import optparse
import textwrap
import inspect


def change_german_salutation():
    """Import german translation json file and change from Du to Sie.

    usage::

        bin/change_german_salutation jsonfile
    """
    usage = 'usage: %prog config_file'
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(inspect.getdoc(change_german_salutation))
    )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2

    jsonfile = args[0]
    data = json.load(open(jsonfile, 'r'))

    regexlist = [
        ('Bitte entschuldige', 'Bitte entschuldigen Sie'),
        ('aktiviere', 'aktivieren Sie'),
        ('registrierst hast', 'registriert haben'),
        ('wechsle', 'wechseln Sie'),
        ('Bitte setze', 'Bitte setzen Sie'),
        ('stimme den', 'stimmen Sie den'),
        ('Ziehe den', 'Ziehen Sie den'),
        ('Gehe', 'Gehen Sie'),
        ('gehe auf', 'gehen Sie auf'),
        ('überprüfe', 'überprüfen Sie'),
        ('kontaktiere', 'kontaktieren Sie'),
        ('schaue', 'schauen Sie'),
        ('Klicke', 'Klicken Sie'),
        ('gib dabei', 'geben Sie dabei'),
        ('Bitte gib', 'Bitte geben Sie'),
        ('Du kannst', 'Sie können'),
        ('Du hast', 'Sie haben'),
        ('Du bist', 'Sie sind'),
        ('Du auf den Aktivierungslink geklickt hast, kannst Du',
            'Sie auf den Aktivierungslink geklickt haben, können Sie'),
        ('Du diese E-Mail nicht erhältst, überprüfe ',
            'Sie diese E-Mail nicht erhalten, überprüfen Sie '),
        ('Du kannst', 'Sie können'),
        ('Du Dich', 'Sie sich'),
        ('Dir', 'Ihnen'),
        ('Dein', 'Ihr'),
        ('überprüfe Deine', 'überprüfen Sie Ihre'),
        ('Deine', 'Ihre'),
        ('Deiner', 'Ihrer')]

    for entry in sorted(data.keys()):
        line = data[entry]
        print(line)
        for regex, replacement in regexlist:
            if re.search(regex, data[entry]):
                line = re.sub(regex, replacement, line)
        if line != data[entry]:
            print(line)
        print('-----------------------------')
        data[entry] = line

    filename = os.path.splitext(jsonfile)[0]
    filename = filename + '_new.json'

    with open(filename, 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
