import AdhEmbedModule = require("../../../Embed/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhResourceAreaModule = require("../../../ResourceArea/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinKiezkassenWorkbenchModule = require("../Workbench/Module");

import AdhEmbed = require("../../../Embed/Embed");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");

import AdhMeinBerlinKiezkassenWorkbench = require("../Workbench/Workbench");

import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");

import Context = require("./Context");


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
