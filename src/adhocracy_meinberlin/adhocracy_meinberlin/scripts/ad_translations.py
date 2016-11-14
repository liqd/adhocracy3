"""Script to change the salutation in german texts."""

import argparse
import inspect
import json
import os
import re
import textwrap


def main():
    """Import german translation json file and change from Du to Sie.

    The result will be saved to a separate file. If the input file is
    ``some/path/file.json`` the output will be saved to
    ``some/path/file_new.json``.

    """
    doc = textwrap.dedent(inspect.getdoc(main))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('jsonfile')
    args = parser.parse_args()

    data = json.load(open(args.jsonfile, 'r'))

    regexlist = [
        ('Bitte erkläre, wieso du diesen Beitrag melden möchtest',
            'Bitte erklären Sie, wieso Sie diesen Beitrag melden möchten'),
        ('enn Du doch einen neuen Link benötigst',
            'enn Sie doch einen neuen Link benötigen'),
        ('benutze den', 'benutzen Sie den'),
        ('gib dabei', 'geben Sie dabei'),
        ('kontaktiere bitte', 'kontaktieren Sie bitte'),
        ('ersuche bitte', 'ersuchen Sie bitte'),
        ('Dich einzuloggen', 'sich einzuloggen'),
        ('schließe bitte das', 'schließen Sie bitte das'),
        ('Wenn Du einem Kommentar inhaltlich widersprechen möchtest',
            'Wenn Sie einem Kommentar inhaltlich widersprechen möchten'),
        ('utze dies', 'utzen Sie dies'),
        ('ähle bitte', 'ählen Sie bitte'),
        ('ähle ein oder mehrere', 'ählen Sie ein oder mehrere'),
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
        ('schaue', 'schauen Sie'),
        ('Klicke', 'Klicken Sie'),
        ('gib dabei', 'geben Sie dabei'),
        ('öchtest Du ', 'öchten Sie '),
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
