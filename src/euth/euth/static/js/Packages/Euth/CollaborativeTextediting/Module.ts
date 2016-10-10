import * as AdhDebateWorkbenchModule from "../../Core/DebateWorkbench/Module";
import * as AdhDebateWorkbench from "../../Core/DebateWorkbench/DebateWorkbench";
import * as AdhProcess from "../../Core/Process/Process";
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
            adhProcessProvider.templates[RIEuthCollaborativeTextProcess.content_type] =
                "<adh-debate-workbench></adh-debate-workbench>";
            adhProcessProvider.templates[RIEuthCollaborativeTextPrivateProcess.content_type] =
                "<adh-debate-workbench></adh-debate-workbench>";
        }])
        .config(["adhConfig", "adhResourceAreaProvider", (adhConfig, adhResourceAreaProvider) => {
            var processHeaderSlot = adhConfig.pkg_path + AdhDebateWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[RIEuthCollaborativeTextProcess.content_type] = processHeaderSlot;
            AdhDebateWorkbench.registerRoutes(RIEuthCollaborativeTextProcess)(adhResourceAreaProvider);
            adhResourceAreaProvider.processHeaderSlots[RIEuthCollaborativeTextPrivateProcess.content_type] = processHeaderSlot;
            AdhDebateWorkbench.registerRoutes(RIEuthCollaborativeTextPrivateProcess)(adhResourceAreaProvider);
        }]);
};
