"""Initialize meinberlin ACM."""
from pyramid.traversal import find_interface
from pyramid.renderers import render

from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.utils import has_annotation_sheet_data
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_meinberlin.resources.bplan import IProposalVersion
from adhocracy_meinberlin.resources.bplan import IProposal
from adhocracy_meinberlin import sheets
from adhocracy_meinberlin import resources


def send_bplan_submission_confirmation_email(event):
    """Notify office worker and creator about created bplan version."""
    if not hasattr(event.registry, 'messenger'):  # ease testing
        return
    messenger = event.registry.messenger
    proposal_version = event.object
    if not _is_proposal_creation_finished(proposal_version):
        return
    appstruct = _get_appstruct(proposal_version, event.registry)
    process_settings = _get_all_process_settings(proposal_version,
                                                 event.registry)
    if process_settings['plan_number'] == 0 or \
            process_settings['office_worker_email'] is None:
        return
    templates_values = _get_templates_values(process_settings, appstruct)
    subject = 'Ihre Stellungnahme zum Bebauungsplan {plan_number}, ' \
              '{participation_kind} von ' \
              '{workflow_state_data_participate[start_date]:%d/%m/%Y} ' \
              '- {workflow_state_data_participate[end_date]:%d/%m/%Y}.' \
              .format(**process_settings)
    messenger.send_mail(subject,
                        [appstruct['email']],
                        'noreply@mein.berlin.de',
                        render('adhocracy_meinberlin:templates/'
                               'bplan_submission_confirmation.txt.mako',
                               templates_values))
    messenger.send_mail(subject,
                        [process_settings['office_worker_email']],
                        'noreply@mein.berlin.de',
                        render('adhocracy_meinberlin:templates/'
                               'bplan_submission_confirmation.txt.mako',
                               templates_values))


def _get_templates_values(process_settings, appstruct):
    templates_values = appstruct.copy()
    templates_values.update(process_settings)
    return templates_values


def _get_all_process_settings(proposal_version, registry):
    process = find_interface(proposal_version, resources.bplan.IProcess)
    process_settings = registry.content.get_sheet(
        process,
        sheets.bplan.IProcessSettings).get()
    process_private_settings = registry.content.get_sheet(
        process,
        sheets.bplan.IProcessPrivateSettings).get()
    all_process_settings = process_settings.copy()
    all_process_settings.update(process_private_settings)
    workflowassignment = registry.content.get_sheet(process,
                                                    IWorkflowAssignment).get()
    state_data = _get_workflow_state_data(workflowassignment['state_data'],
                                          'participate')
    all_process_settings.update(
        {'workflow_state_data_participate': state_data})
    return all_process_settings


def _get_workflow_state_data(state_data_list: [],
                             workflow_name: str):
    for state_data in state_data_list:  # pragma: no branch
        if state_data['name'] == workflow_name:  # pragma: no branch
            return state_data


def _get_appstruct(proposal_version, registry):
    proposal_sheet = registry.content.get_sheet(proposal_version,
                                                sheets.bplan.IProposal)
    appstruct = proposal_sheet.get()
    return appstruct


def _is_proposal_creation_finished(proposal_version):
    proposal_item = find_interface(proposal_version, IProposal)
    versions_with_data = [x for x in proposal_item.values()
                          if IProposalVersion.providedBy(x)
                          and has_annotation_sheet_data(x)]
    return len(versions_with_data) == 1


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(send_bplan_submission_confirmation_email,
                          IResourceCreatedAndAdded,
                          object_iface=IProposalVersion)
    config.add_subscriber(send_bplan_submission_confirmation_email,
                          IResourceSheetModified,
                          object_iface=IProposalVersion)
