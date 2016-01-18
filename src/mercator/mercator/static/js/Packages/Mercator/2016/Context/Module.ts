import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import RIProcess from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IProcess";

import * as Workbench from "../Workbench/Workbench";
import * as Context from "./Context";


export var moduleName = "adhMercator2016Context";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMercator2016ContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", Context.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("mercator2016", ["mercator2016"]);
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider.template("mercator2016", ["adhConfig", "$templateRequest", Context.areaTemplate]);
            Workbench.registerRoutes(
                RIProcess.content_type,
                "mercator2016"
            )(adhResourceAreaProvider);
        }]);
};
