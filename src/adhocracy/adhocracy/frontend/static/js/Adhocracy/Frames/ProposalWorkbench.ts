declare var $;

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