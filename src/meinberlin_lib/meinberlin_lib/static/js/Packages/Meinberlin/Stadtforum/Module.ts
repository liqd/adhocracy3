import * as AdhMeinberlinStadtforumProcessModule from "./Process/Module";
import * as AdhMeinberlinStadtforumProposalModule from "./Proposal/Module";


export var moduleName = "adhMeinberlinStadtforum";

export var register = (angular) => {
    AdhMeinberlinStadtforumProcessModule.register(angular);
    AdhMeinberlinStadtforumProposalModule.register(angular);

    angular
        .module(moduleName, [
            AdhMeinberlinStadtforumProcessModule.moduleName,
            AdhMeinberlinStadtforumProposalModule.moduleName,
        ]);
};
