import AdhEmbedModule = require("../../../Embed/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinBurgerhaushaltWorkbenchModule = require("../Workbench/Module");

import AdhEmbed = require("../../../Embed/Embed");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");

import AdhMeinBerlinBurgerhaushaltWorkbench = require("../Workbench/Workbench");

import RIBurgerhaushaltProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess");

import Context = require("./Context");


export var moduleName = "adhMeinBerlinBurgerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinBerlinBurgerhaushaltWorkbenchModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhBurgerhaushaltContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", Context.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("burgerhaushalt");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider.template("burgerhaushalt", ["adhConfig", "$templateRequest", Context.areaTemplate]);
            AdhMeinBerlinBurgerhaushaltWorkbench.registerRoutes(
                RIBurgerhaushaltProcess.content_type,
                "burgerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
