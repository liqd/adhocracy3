import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhMeinberlinAlexanderplatzWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhMapping from "../../../Mapping/Mapping";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinAlexanderplatzWorkbench from "../Workbench/Workbench";

import RIAlexanderplatzProcess from "../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";

import * as AdhMeinberlinAlexanderplatzContext from "./Context";


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
            adhResourceAreaProvider
                .template("alexanderplatz", ["adhConfig", "$templateRequest", AdhMeinberlinAlexanderplatzContext.areaTemplate]);
            AdhMeinberlinAlexanderplatzWorkbench.registerRoutes(processType, "alexanderplatz")(adhResourceAreaProvider);
        }])
        .config(["adhMapDataProvider", (adhMapDataProvider: AdhMapping.MapDataProvider) => {
            adhMapDataProvider.icons["document"] = {
                className: "icon-board-pin",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
            adhMapDataProvider.icons["document-selected"] = {
                className: "icon-board-pin is-active",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
        }]);
};
