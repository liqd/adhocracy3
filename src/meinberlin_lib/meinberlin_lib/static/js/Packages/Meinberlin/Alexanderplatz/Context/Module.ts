import * as AdhEmbedModule from "../../../Core/Embed/Module";
import * as AdhResourceAreaModule from "../../../Core/ResourceArea/Module";

import * as AdhMeinberlinAlexanderplatzWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Core/Embed/Embed";
import * as AdhResourceArea from "../../../Core/ResourceArea/ResourceArea";

import * as AdhMeinberlinAlexanderplatzWorkbench from "../Workbench/Workbench";

import RIAlexanderplatzProcess from "../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";


export var moduleName = "adhMeinberlinAlexanderplatzContext";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinAlexanderplatzWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("alexanderplatz");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider: AdhResourceArea.Provider) => {
            AdhMeinberlinAlexanderplatzWorkbench.registerRoutes(processType, "alexanderplatz")(adhResourceAreaProvider);
        }]);
};
