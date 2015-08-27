import AdhS1Context = require("./Context/Context");
import AdhS1Proposal = require("./Proposal/Proposal");
import AdhS1Workbench = require("./Workbench/Workbench");


export var moduleName = "adhS1";

export var register = (angular) => {
    AdhS1Context.register(angular);
    AdhS1Proposal.register(angular);
    AdhS1Workbench.register(angular);

    angular
        .module(moduleName, [
            AdhS1Context.moduleName,
            AdhS1Proposal.moduleName,
            AdhS1Workbench.moduleName
        ]);
};
