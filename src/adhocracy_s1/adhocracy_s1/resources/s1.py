# -*- encoding: utf-8 -*-

"""Resource types for s1 process."""
from pyramid.registry import Registry

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.resources.logbook import add_logbook_service
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.logbook import IHasLogbookPool
from adhocracy_core.utils import get_matching_isheet


DEFAULT_DESCRIPTION = '''\
# Was man hier machen kann

Mit Agenda S-1 werden keine Entscheidungsprozesse auf den Kopf gestellt. Es gibt aber eine neue, einfache Möglichkeit Themen sichtbarer zu machen, die viele Mitarbeiterinnen und Mitarbeiter beschäftigen.

1.  **Machen Sie einen Vorschlag**, welches Thema Sie gern von der Geschäftsleitung diskutiert sehen würden. Formulieren Sie so, dass eine offene Diskussion möglich ist. Oft genug wissen Ihre Kolleginnen und Kollegen schon nach einer aussagekräftigen Überschrift um was es geht. Im Textkörper bietet sich die Gelegenheit den Sachverhalt auch für Nicht-Eingeweihte darzustellen. Machen Sie bei Bedarf einen Vorschlag, wer das Thema präsentieren sollte vor der Geschäftsleitung oder bieten Sie an, dass Sie diese Rolle bereit wären, zu übernehmen.

    Beispiel: *„Parkplatz-Situation: Durch die Baustelle sind mindestens noch 5 Monate Engpässe zu erwarten. Die Parkplätze für Gäste sind zahlreich und meist leer. Gibt es eine Möglichkeit, einen Teil der Gästeparkplätze umzuwidmen für den Zeitraum der Baumaßnahmen oder andere Ideen der Parkplatzsituation Herr zu werden? Ich kann gerne die Diskussion zusammenfassen und selber bei der Sitzung vorstellen.“*

    Wichtig ist, dass ab drei Tage vor der Geschäftsleitungs-Sitzung keine neuen Vorschläge für diese Sitzung mehr eingebracht werden können. Von diesem Zeitpunkt an, kann über die Vorschläge nur noch abgestimmt werden.

    Wenn Sie zu diesem Zeitpunkt aber bereits einen weiteren Themenvorschlag machen möchten, dann wird dieser einfach in die nächste Periode, also für die übernächste Geschäftsleitungssitzung gespeichert. **Sie haben also immer die Möglichkeit Vorschläge anzulegen**.


2.  **Diskutieren Sie** mit bei Ihren Themenvorschlägen und denen Ihrer Kolleginnen und Kollegen. Zögern Sie nicht, Lösungvorschläge einzubringen oder Details zum Sachverhalt bei zu steuern. Ihre Beiträge erlauben Kolleginnen und Kollegen sich ebenfalls zu informieren und später der Geschäftsleitung eine bessere Entscheidungsgrundlage zu geben. Beiträge, die Sie für besonders wertvoll für die Debatte betrachten, können Sie mit einem Klick als relevant markieren. Das ist die kleine Zahl rechts in der Ecke jeden Beitrags.

3.  **Stimmen Sie über die Themenvorschläge ab**. Sie können zu jeder Zeit Themenvorschläge, die Sie gerne auf der Tagesordnung der Geschäftsleitung sähen, mit Ihrer Stimme versehen. Dabei ist es Ihnen freigestellt, nur den Ihnen wichtigsten Vorschlag zu unterstützen, oder alle, die Sie als wichtig erachten. Am Ende schafft es der Themenvorschlag mit den meisten Unterstützern auf die Tagesordnung. Unterlegene Vorschläge können aber in der Folgeperiode, also für die nächste Sitzung neu ins Rennen gehen.

Die Abstimmung endet zwei Tage vor der Geschäftsleitungs-Sitzung. Das gibt der Geschäftsleitung, dem Personalrat und demjenigen, der das Thema vorstellt, Zeit sich vorzubereiten und auch die Diskussion zu dem Vorschlag für die Geschäftsleitung zusammenzufassen.

## PHASEN:

Eine Entscheidungsperiode - die Vorbereitung einer Sitzung - besteht aus drei Phasen:

1.  **Vorschläge anlegen und bewerten**
    Sie können Vorschläge angelegen, und diese auch direkt diskutieren und bewerten.

2.  **Vorschläge bewerten**
    Zu diesem Zeitpunkt - etwa zwei oder drei Tage vor er nächsten Sitzung - können Sie keine Vorschläge mehr anlegen. Sie haben aber noch Zeit zum bewerten von Vorschlägen.

3.  **Gewinner zeigen**    Der von Mitarbeitenden am Besten bewertete Vorschlag wird als Gewinner gekennzeichnet. Die Diskussion und Abstimmung ist beendet für diese Periode.
    Dafür läuft bereits die Phase “Vorschläge anlegen” für die folgende Periode, also die übernächste Sitzung.
'''


SHORT_DESCRIPTION = '''\
# Willkomen auf Agenda S-1 - der Punkt vor Sonstiges:

Wir freuen uns, Sie auf der Beteiligungsplatform Ihrer Organisation willkommen heißen zu dürfen. Agenda S-1 gibt Ihnen die Möglichkeit, die Themen, die Ihnen wichtig sind, auf die Tagesordnung der nächsten Geschäftsleitungs-Sitzung zu bringen. Mit Ihren Kolleginnen und Kollegen können Sie die Vorschläge diskutieren und mit einem einfachen Klick diejenigen unterstützen, die Sie auf der Tagesordnung sehen wollen. Der Gewinner-Vorschlag wird automatisch der letzte Punkt auf der Agenda: S-1, der Punkt vor Sonstiges.
'''


def set_default_description(context: process.IProcess, registry: Registry,
                            **kwargs):
    """Set default S1 description text."""
    isheet = get_matching_isheet(context, IDescription)
    sheet = registry.content.get_sheet(context, isheet)
    appstruct = {
        'description': DEFAULT_DESCRIPTION,
        'short_description': SHORT_DESCRIPTION,
    }
    sheet.set(appstruct, omit_readonly=False)


class IProcess(process.IProcess):
    """S1 participation process."""


process_meta = process.process_meta._replace(
    content_name='S1Process',
    iresource=IProcess,
    default_workflow='s1',
    alternative_workflows=('s1_private',
                           ))\
    ._add(after_creation=(set_default_description,))


class IProposalVersion(proposal.IProposalVersion):
    """S1 participation process content version."""


proposal_version_meta = proposal.proposal_version_meta\
    ._replace(iresource=IProposalVersion,
              )\
    ._add(extended_sheets=(IHasLogbookPool,
                           ))


class IProposal(proposal.IProposal):
    """S1 participation process content."""


proposal_meta = proposal.proposal_meta\
    ._replace(iresource=IProposal,
              element_types=(IProposalVersion,),
              item_type=IProposalVersion,
              autonaming_prefix = 'proposal_',
              default_workflow = 's1_content',
              )\
    ._add(after_creation=(add_logbook_service,))


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
