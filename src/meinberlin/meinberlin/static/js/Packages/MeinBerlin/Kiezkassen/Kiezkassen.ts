import AdhMeinBerlinKiezkassenContext = require("./Context/Context");
import AdhMeinBerlinKiezkassenProcess = require("./Process/Process");
import AdhMeinBerlinKiezkassenWorkbench = require("./Workbench/Workbench");
import AdhMeinBerlinProposal = require("../../Proposal/Proposal");


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenContext.register(angular);
    AdhMeinBerlinKiezkassenProcess.register(angular);
    AdhMeinBerlinKiezkassenWorkbench.register(angular);
    AdhMeinBerlinProposal.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenContext.moduleName,
            AdhMeinBerlinKiezkassenProcess.moduleName,
            AdhMeinBerlinKiezkassenWorkbench.moduleName,
            AdhMeinBerlinProposal.moduleName
        ]);
};
