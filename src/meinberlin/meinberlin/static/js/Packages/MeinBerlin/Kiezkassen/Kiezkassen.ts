import AdhMeinBerlinKiezkassenProcess = require("./Process/Process");
import AdhMeinBerlinKiezkassenProposal = require("./Proposal/Proposal");
import AdhMeinBerlinKiezkassenWorkbench = require("./Workbench/Workbench");


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenProcess.register(angular);
    AdhMeinBerlinKiezkassenProposal.register(angular);
    AdhMeinBerlinKiezkassenWorkbench.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenProcess.moduleName,
            AdhMeinBerlinKiezkassenProposal.moduleName,
            AdhMeinBerlinKiezkassenWorkbench.moduleName
        ]);
};
