import AdhMeinBerlinKiezkassenProcess = require("./Process/Process");
import AdhMeinBerlinKiezkassenProposal = require("./Proposal/Proposal");


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenProcess.register(angular);
    AdhMeinBerlinKiezkassenProposal.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenProcess.moduleName,
            AdhMeinBerlinKiezkassenProposal.moduleName
        ]);
};
