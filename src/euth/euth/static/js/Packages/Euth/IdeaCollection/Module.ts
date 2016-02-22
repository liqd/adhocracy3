import * as AdhEuthIdeaProposalModule from "./Proposal/Module";
import * as AdhEuthIdeaContextModule from "./Context/Module";
import * as AdhEuthIdeaWorkbenchModule from "./Workbench/Module";

export var moduleName = "adhEuthIdeaCollection";

export var register = (angular) => {
    AdhEuthIdeaProposalModule.register(angular);
    AdhEuthIdeaWorkbenchModule.register(angular);
    AdhEuthIdeaContextModule.register(angular);

    angular
        .module(moduleName, [
            AdhEuthIdeaProposalModule.moduleName,
            AdhEuthIdeaWorkbenchModule.moduleName,
            AdhEuthIdeaContextModule.moduleName
        ]);
};
