import AdhMeinBerlinBplaeneProposalModule = require("./Proposal/Module");

export var moduleName = "adhMeinBerlinBplaene";

export var register = (angular) => {
    AdhMeinBerlinBplaeneProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinBplaeneProposalModule.moduleName
        ]);
};
