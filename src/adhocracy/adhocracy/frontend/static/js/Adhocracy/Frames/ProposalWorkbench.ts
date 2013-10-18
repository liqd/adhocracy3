declare var $;
declare var obviel;
declare var obvieltemplate;

var some_local_variable = "hey there..";

export function init() {
    $("#proposal_workbench_detail").text("...");
    $("#proposal_workbench_directory").text("...");
    $("#proposal_workbench_discussion").text("...");

    console.log("module Adhocracy/Frames/ProposalWorkbench loaded.");
};

export function something_pure(i: number): number {
    return i/2;
}

export function open_proposals(uri) {

    // three skill levels:

    /* // 1. create dom elements by hand

    $('#proposal_workbench_directory')[0].textContent = '';
    $('<ol><li>proposal DAG 1</li><li>proposal DAG 1</li></ol>').appendTo($('#proposal_workbench_directory'));

    */


    // 2. create json objects by hand and render them using obviel

    var proposal_dags = [{
        "path": "/adhocracy/0",
        "data": {
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "proposal DAG 1"
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "content_type": "adhocracy.contents.interfaces.IProposalContainer"
    }, {
        "path": "/adhocracy/0",
        "data": {
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "proposal DAG 1"
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "content_type": "adhocracy.contents.interfaces.IProposalContainer"
    }]

    var proposal_dags_with_cheating = [{
        ifaces: ['IName'],
        meta: { path: '...' },
        data: { 'adhocracy#interfaces#IName': { name: 'proposal DAG 1' } },
    }, {
        ifaces: ['IName'],
        meta: { path: '...' },
        data: { 'adhocracy#interfaces#IName': { name: 'proposal DAG 1' } },
    }]

    obviel.view({
        iface: 'IName',
        obvtUrl: 'templates/IName.small.obvt',
    });

    $('#proposal_workbench_directory')[0].textContent = '';
    $('#proposal_workbench_directory').render(proposal_dags_with_cheating[0]);

    // FIXME: create a proposal list from template.


    // 3. fetch json objects via ajax.




}
