import * as AdhEmbedModule from "../../Embed/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhResourceAreaModule from "../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as AdhPcompassWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../Embed/Embed";
import * as AdhResourceArea from "../../ResourceArea/ResourceArea";

import * as AdhPcompassWorkbench from "../Workbench/Workbench";

import RIPcompassProcess from "../../../Resources_/adhocracy_pcompass/resources/pcompass/IProcess";

import * as Context from "./Context";


export var moduleName = "adhPcompassContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhPcompassWorkbenchModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhPcompassContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", Context.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("pcompass");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider.template("pcompass", ["adhConfig", "$templateRequest", Context.areaTemplate]);
            AdhPcompassWorkbench.registerRoutes(
                RIPcompassProcess.content_type,
                "pcompass"
            )(adhResourceAreaProvider);
        }]);
};
