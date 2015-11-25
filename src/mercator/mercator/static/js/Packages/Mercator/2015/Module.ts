import * as AdhMercator2015ProposalModule from "./Proposal/Module";
import * as AdhMercator2015WorkbenchModule from "./Workbench/Module";


export var moduleName = "adhMercator2015";

export var register = (angular) => {
    AdhMercator2015ProposalModule.register(angular);
    AdhMercator2015WorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhMercator2015ProposalModule.moduleName,
            AdhMercator2015WorkbenchModule.moduleName
        ]);
};
