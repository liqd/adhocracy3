import AdhMeinBerlinBplaeneProposal = require("./Proposal/Proposal");

export var moduleName = "adhMeinBerlinBplaene";

export var register = (angular) => {
    AdhMeinBerlinBplaeneProposal.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinBplaeneProposal.moduleName
        ]);
};
