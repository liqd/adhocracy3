import * as AdhDebateWorkbenchModule from "../../DebateWorkbench/Module";
import * as AdhDebateWorkbench from "../../DebateWorkbench/DebateWorkbench";
import * as AdhProcess from "../../Process/Process";
import RIEuthCollaborativeTextProcess from "../../../Resources_/adhocracy_euth/resources/collaborative_text/IProcess";

export var moduleName = "euthCollaberativeTextediting";

export var register = (angular) => {

    AdhDebateWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhDebateWorkbenchModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider: AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIEuthCollaborativeTextProcess.content_type] = ["$q", ($q: angular.IQService) => {
                return $q.when("<adh-debate-workbench></adh-debate-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", AdhDebateWorkbench.registerRoutes(RIEuthResourcesCollaborativeTextIProcess)]);
        };
