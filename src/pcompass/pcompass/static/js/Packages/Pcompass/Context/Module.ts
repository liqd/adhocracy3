import * as AdhEmbedModule from "../../Embed/Module";
import * as AdhResourceAreaModule from "../../ResourceArea/Module";

import * as AdhPcompassWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../Embed/Embed";
import * as AdhResourceArea from "../../ResourceArea/ResourceArea";

import * as AdhPcompassWorkbench from "../Workbench/Workbench";

import RIPcompassProcess from "../../../Resources_/adhocracy_pcompass/resources/request/IProcess";


export var moduleName = "adhPcompassContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhPcompassWorkbenchModule.moduleName,
            AdhResourceAreaModule.moduleName,
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("pcompass");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            AdhPcompassWorkbench.registerRoutes(
                RIPcompassProcess.content_type,
                "pcompass"
            )(adhResourceAreaProvider);
        }]);
};
