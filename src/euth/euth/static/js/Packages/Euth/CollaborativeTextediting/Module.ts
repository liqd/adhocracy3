import * as AdhDebateWorkbenchModule from "../../DebateWorkbench/Module";
import * as AdhDebateWorkbench from "../../DebateWorkbench/DebateWorkbench";
import * as AdhProcess from "../../Process/Process";
import RIEuthCollaborativeTextProcess from "../../../Resources_/adhocracy_euth/resources/collaborative_text/IProcess";
import RIEuthCollaborativeTextPrivateProcess from "../../../Resources_/adhocracy_euth/resources/collaborative_text/IPrivateProcess";

export var moduleName = "adhEuthCollaberativeTextediting";

export var register = (angular) => {

    AdhDebateWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhDebateWorkbenchModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider: AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIEuthCollaborativeTextProcess.content_type] =
                "<adh-debate-workbench></adh-debate-workbench>";
            adhProcessProvider.templateFactories[RIEuthCollaborativeTextPrivateProcess.content_type] =
                "<adh-debate-workbench></adh-debate-workbench>";
        }])
        .config(["adhResourceAreaProvider", AdhDebateWorkbench.registerRoutes(RIEuthCollaborativeTextProcess)])
        .config(["adhResourceAreaProvider", AdhDebateWorkbench.registerRoutes(RIEuthCollaborativeTextPrivateProcess)]);
};
