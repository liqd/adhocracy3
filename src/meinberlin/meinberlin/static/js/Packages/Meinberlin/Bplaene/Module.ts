import * as AdhMeinberlinBplaeneProposalModule from "./Proposal/Module";

export var moduleName = "adhMeinberlinBplaene";

export var register = (angular) => {
    AdhMeinberlinBplaeneProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBplaeneProposalModule.moduleName
        ]);
};
