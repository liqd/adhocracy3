import AdhEmbedModule = require("../../../Embed/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinAlexanderplatzWorkbenchModule = require("../Workbench/Module");

import AdhEmbed = require("../../../Embed/Embed");
import AdhMapping = require("../../../Mapping/Mapping");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");

import AdhMeinBerlinAlexanderplatzWorkbench = require("../Workbench/Workbench");

import RIAlexanderplatzProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess");

import AdhMeinBerlinAlexanderplatzContext = require("./Context");


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
