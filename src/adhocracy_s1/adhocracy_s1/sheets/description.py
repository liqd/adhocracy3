"""Description Sheet with default content for the s1 process."""
from colander import deferred
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Text
from adhocracy_core.sheets.description import description_meta
from adhocracy_s1.resources.s1 import IProcess


DEFAULT_S1_SHORT_DESCRIPTION = '''\
# Willkomen auf Agenda S-1 - der Punkt vor Sonstiges:

Wir freuen uns, Sie auf der Beteiligungsplatform Ihrer Organisation willkommen
heißen zu dürfen. Agenda S-1 gibt Ihnen die Möglichkeit, die Themen, die Ihnen
wichtig sind, auf die Tagesordnung der nächsten Geschäftsleitungs-Sitzung zu
bringen. Mit Ihren Kolleginnen und Kollegen können Sie die Vorschläge
diskutieren und mit einem einfachen Klick diejenigen unterstützen, die Sie auf
der Tagesordnung sehen wollen. Der Gewinner-Vorschlag wird automatisch der
letzte Punkt auf der Agenda: S-1, der Punkt vor Sonstiges.
'''


DEFAULT_S1_DESCRIPTION = '''\
# Was man hier machen kann

Mit Agenda S-1 werden keine Entscheidungsprozesse auf den Kopf gestellt. Es
gibt aber eine neue, einfache Möglichkeit Themen sichtbarer zu machen, die
viele Mitarbeiterinnen und Mitarbeiter beschäftigen.

1.  **Machen Sie einen Vorschlag**, welches Thema Sie gern von der
    Geschäftsleitung diskutiert sehen würden. Formulieren Sie so, dass eine
    offene Diskussion möglich ist. Oft genug wissen Ihre Kolleginnen und
    Kollegen schon nach einer aussagekräftigen Überschrift um was es geht. Im
    Textkörper bietet sich die Gelegenheit den Sachverhalt auch für
    Nicht-Eingeweihte darzustellen.  Machen Sie bei Bedarf einen Vorschlag, wer
    das Thema präsentieren sollte vor der Geschäftsleitung oder bieten Sie an,
    dass Sie diese Rolle bereit wären, zu übernehmen.

    Beispiel: *„Parkplatz-Situation: Durch die Baustelle sind mindestens noch 5
    Monate Engpässe zu erwarten. Die Parkplätze für Gäste sind zahlreich und
    meist leer. Gibt es eine Möglichkeit, einen Teil der Gästeparkplätze
    umzuwidmen für den Zeitraum der Baumaßnahmen oder andere Ideen der
    Parkplatzsituation Herr zu werden? Ich kann gerne die Diskussion
    zusammenfassen und selber bei der Sitzung vorstellen.“*

    Wichtig ist, dass ab drei Tage vor der Geschäftsleitungs-Sitzung keine
    neuen Vorschläge für diese Sitzung mehr eingebracht werden können. Von
    diesem Zeitpunkt an, kann über die Vorschläge nur noch abgestimmt werden.

    Wenn Sie zu diesem Zeitpunkt aber bereits einen weiteren Themenvorschlag
    machen möchten, dann wird dieser einfach in die nächste Periode, also für
    die übernächste Geschäftsleitungssitzung gespeichert. **Sie haben also
    immer die Möglichkeit Vorschläge anzulegen**.

2.  **Diskutieren Sie** mit bei Ihren Themenvorschlägen und denen Ihrer
    Kolleginnen und Kollegen. Zögern Sie nicht, Lösungvorschläge einzubringen
    oder Details zum Sachverhalt bei zu steuern. Ihre Beiträge erlauben
    Kolleginnen und Kollegen sich ebenfalls zu informieren und später der
    Geschäftsleitung eine bessere Entscheidungsgrundlage zu geben. Beiträge,
    die Sie für besonders wertvoll für die Debatte betrachten, können Sie mit
    einem Klick als relevant markieren. Das ist die kleine Zahl rechts in der
    Ecke jeden Beitrags.

3.  **Stimmen Sie über die Themenvorschläge ab**. Sie können zu jeder Zeit
    Themenvorschläge, die Sie gerne auf der Tagesordnung der Geschäftsleitung
    sähen, mit Ihrer Stimme versehen. Dabei ist es Ihnen freigestellt, nur den
    Ihnen wichtigsten Vorschlag zu unterstützen, oder alle, die Sie als wichtig
    erachten. Am Ende schafft es der Themenvorschlag mit den meisten
    Unterstützern auf die Tagesordnung. Unterlegene Vorschläge können aber in
    der Folgeperiode, also für die nächste Sitzung neu ins Rennen gehen.

Die Abstimmung endet zwei Tage vor der Geschäftsleitungs-Sitzung. Das gibt der
Geschäftsleitung, dem Personalrat und demjenigen, der das Thema vorstellt, Zeit
sich vorzubereiten und auch die Diskussion zu dem Vorschlag für die
Geschäftsleitung zusammenzufassen.

## PHASEN:

Eine Entscheidungsperiode - die Vorbereitung einer Sitzung - besteht aus drei
Phasen:

1.  **Vorschläge anlegen und bewerten** Sie können Vorschläge angelegen, und
    diese auch direkt diskutieren und bewerten.

2.  **Vorschläge bewerten** Zu diesem Zeitpunkt - etwa zwei oder drei Tage vor
    er nächsten Sitzung - können Sie keine Vorschläge mehr anlegen. Sie haben
    aber noch Zeit zum bewerten von Vorschlägen.

3.  **Gewinner zeigen**    Der von Mitarbeitenden am Besten bewertete Vorschlag
    wird als Gewinner gekennzeichnet. Die Diskussion und Abstimmung ist beendet
    für diese Periode.  Dafür läuft bereits die Phase “Vorschläge anlegen” für
    die folgende Periode, also die übernächste Sitzung.
'''


@deferred
def deferred_default_short_description(node: MappingSchema, kw: dict) -> str:
    """Return default s1  short description for `context` resource."""
    creating = kw['creating']
    context = kw['context']
    is_process = IProcess.providedBy(context)
    is_creating_process = creating and creating.iresource == IProcess
    if is_process or is_creating_process:
        return DEFAULT_S1_SHORT_DESCRIPTION
    else:
        return ''


@deferred
def deferred_default_description(node: MappingSchema, kw: dict) -> str:
    """Return default s1 description for `context` resource."""
    creating = kw['creating']
    context = kw['context']
    is_process = IProcess.providedBy(context)
    is_creating_process = creating and creating.iresource == IProcess
    if is_process or is_creating_process:
        return DEFAULT_S1_DESCRIPTION
    else:
        return ''


class DescriptionSchema(MappingSchema):
    """S1 Description sheet data structure.

    `short_description`: teaser text for listings, html description etc.
    `description`: a full description
    """

    short_description = Text(default=deferred_default_short_description)
    description = Text(default=deferred_default_description)


description_meta = description_meta._replace(schema_class=DescriptionSchema,
                                             )


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(description_meta, config.registry)
