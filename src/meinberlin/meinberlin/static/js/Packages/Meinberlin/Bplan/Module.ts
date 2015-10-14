import * as AdhMeinberlinBplanProposalModule from "./Proposal/Module";

export var moduleName = "adhMeinberlinBplan";

export var register = (angular) => {
    AdhMeinberlinBplanProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBplanProposalModule.moduleName
        ]);
};
