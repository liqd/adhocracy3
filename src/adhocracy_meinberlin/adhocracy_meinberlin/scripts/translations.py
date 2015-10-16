"""Change the salutation in german texts.

The function change_german_salutation is registered in setup.py
in setup.py.
"""

import argparse
import inspect
import json
import os
import re
import textwrap


def change_german_salutation():
    """Import german translation json file and change from Du to Sie.

    The result will be saved to a separate file. If the input file is
    ``some/path/file.json`` the output will be saved to
    ``some/path/file_new.json``.

    """
    doc = textwrap.dedent(inspect.getdoc(change_german_salutation))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('jsonfile')
    args = parser.parse_args()

    data = json.load(open(args.jsonfile, 'r'))

    regexlist = [
        ('ähle ein Badge', 'ählen Sie ein Badge'),
        ('erstelle ein ', 'erstellen Sie ein '),
        ('Bitte entschuldige', 'Bitte entschuldigen Sie'),
        ('bekommst Du an Deine', 'bekommen Sie an Ihre'),
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
        ('Du diese E-Mail nicht erhältst',
            'Sie diese E-Mail nicht erhalten'),
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

    filename = os.path.splitext(args.jsonfile)[0]
    filename = filename + '_new.json'

    with open(filename, 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
