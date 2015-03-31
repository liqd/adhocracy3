import AdhMeinBerlinKiezkassenProposal = require("./Proposal/Proposal");


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenProposal.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenProposal.moduleName
        ]);
};
