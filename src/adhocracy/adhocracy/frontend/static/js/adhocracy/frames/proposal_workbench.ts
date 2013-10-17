// compile thusly:
// $ nmp install -g typescript
// $ tsc <module>.ts
// more info at http://www.typescriptlang.org/

declare var $;

module adhocracy.frames.proposal_workbench {
    var some_local_variable = "hey there..";

    export function init() {
        $("#proposal_workbench_detail").text("...");
        $("#proposal_workbench_directory").text("...");
        $("#proposal_workbench_discussion").text("...");

        console.log("module proposal_workbench loaded.");
        return;
    };
}
