import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinberlinBuergerhaushaltWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinBuergerhaushaltWorkbench from "../Workbench/Workbench";

import RIBuergerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";

import * as Context from "./Context";


export var moduleName = "adhMeinberlinBuergerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinBuergerhaushaltWorkbenchModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhBuergerhaushaltContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", Context.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("buergerhaushalt");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider.template("buergerhaushalt", ["adhConfig", "$templateRequest", Context.areaTemplate]);
            AdhMeinberlinBuergerhaushaltWorkbench.registerRoutes(
                RIBuergerhaushaltProcess.content_type,
                "buergerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
