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
    // 1. create dom elements by hand
    // 2. create json objects by hand and render them using obviel
    // 3. fetch json objects via ajax.

    $('#proposal_workbench_directory')[0].textContent = '';
    $('<ol><li>proposal DAG 1</li><li>proposal DAG 1</li></ol>').appendTo($('#proposal_workbench_directory'));

}
