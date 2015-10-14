import * as AdhMeinberlinBplanProcessModule from "./Process/Module";
import * as AdhMeinberlinBplanProposalModule from "./Proposal/Module";

export var moduleName = "adhMeinberlinBplan";


export var register = (angular) => {
    AdhMeinberlinBplanProcessModule.register(angular);
    AdhMeinberlinBplanProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinBplanProcessModule.moduleName,
            AdhMeinberlinBplanProposalModule.moduleName
        ]);
};
