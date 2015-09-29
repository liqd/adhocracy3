import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinberlinBurgerhaushaltWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinBurgerhaushaltWorkbench from "../Workbench/Workbench";

import RIBurgerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";

import * as Context from "./Context";


export var moduleName = "adhMeinberlinBurgerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinBurgerhaushaltWorkbenchModule.moduleName,
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
            AdhMeinberlinBurgerhaushaltWorkbench.registerRoutes(
                RIBurgerhaushaltProcess.content_type,
                "burgerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
