import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinBerlinAlexanderplatzWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhMapping from "../../../Mapping/Mapping";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinBerlinAlexanderplatzWorkbench from "../Workbench/Workbench";

import RIAlexanderplatzProcess from "../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess";

import * as AdhMeinBerlinAlexanderplatzContext from "./Context";


export var moduleName = "adhMeinBerlinAlexanderplatzContext";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinBerlinAlexanderplatzWorkbenchModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhAlexanderplatzContextHeader", [
            "adhConfig", "adhPermissions", "adhTopLevelState", AdhMeinBerlinAlexanderplatzContext.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("alexanderplatz");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider: AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("alexanderplatz", ["adhConfig", "$templateRequest", AdhMeinBerlinAlexanderplatzContext.areaTemplate]);
            AdhMeinBerlinAlexanderplatzWorkbench.registerRoutes(processType, "alexanderplatz")(adhResourceAreaProvider);
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
