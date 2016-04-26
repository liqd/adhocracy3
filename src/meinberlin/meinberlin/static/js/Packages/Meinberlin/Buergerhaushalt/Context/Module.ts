import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhMeinberlinBuergerhaushaltWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinBuergerhaushaltWorkbench from "../Workbench/Workbench";

import RIBuergerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";


export var moduleName = "adhMeinberlinBuergerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinBuergerhaushaltWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("buergerhaushalt", ["burgerhaushalt"]);
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            AdhMeinberlinBuergerhaushaltWorkbench.registerRoutes(
                RIBuergerhaushaltProcess.content_type,
                "buergerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
