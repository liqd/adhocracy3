import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhMeinberlinKiezkasseWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinKiezkasseWorkbench from "../Workbench/Workbench";

import RIKiezkasseProcess from "../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";


export var moduleName = "adhMeinberlinKiezkasseContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinKiezkasseWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkasse", ["kiezkassen"]);
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            AdhMeinberlinKiezkasseWorkbench.registerRoutes(
                RIKiezkasseProcess.content_type,
                "kiezkasse"
            )(adhResourceAreaProvider);
        }]);
};
