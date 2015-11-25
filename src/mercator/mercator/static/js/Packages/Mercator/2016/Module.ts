import * as AdhMercator2016ProposalModule from "./Proposal/Module";


export var moduleName = "adhMercator2016";

export var register = (angular) => {
    AdhMercator2016ProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMercator2016ProposalModule.moduleName
        ]);
};
