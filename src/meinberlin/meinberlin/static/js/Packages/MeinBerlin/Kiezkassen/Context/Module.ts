import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinBerlinKiezkassenWorkbenchModule from "../Workbench/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinBerlinKiezkassenWorkbench from "../Workbench/Workbench";

import RIKiezkassenProcess from "../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";

import * as Context from "./Context";


export var moduleName = "adhMeinBerlinKiezkassenContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinBerlinKiezkassenWorkbenchModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhKiezkassenContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", Context.headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkassen");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider.template("kiezkassen", ["adhConfig", "$templateRequest", Context.areaTemplate]);
            AdhMeinBerlinKiezkassenWorkbench.registerRoutes(
                RIKiezkassenProcess.content_type,
                "kiezkassen"
            )(adhResourceAreaProvider);
        }]);
};
