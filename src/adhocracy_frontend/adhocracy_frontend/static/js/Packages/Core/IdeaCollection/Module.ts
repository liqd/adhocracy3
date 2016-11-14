import * as AdhIdeaCollectionPollModule from "./Poll/Module";
import * as AdhIdeaCollectionProcessModule from "./Process/Module";
import * as AdhIdeaCollectionProposalModule from "./Proposal/Module";
import * as AdhIdeaCollectionWorkbenchModule from "./Workbench/Module";

export var moduleName = "adhIdeaCollection";

export var register = (angular) => {
    AdhIdeaCollectionPollModule.register(angular);
    AdhIdeaCollectionProcessModule.register(angular);
    AdhIdeaCollectionProposalModule.register(angular);
    AdhIdeaCollectionWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhIdeaCollectionPollModule.moduleName,
            AdhIdeaCollectionProcessModule.moduleName,
            AdhIdeaCollectionProposalModule.moduleName,
            AdhIdeaCollectionWorkbenchModule.moduleName
        ]);
};
