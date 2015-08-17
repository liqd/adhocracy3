import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");

import AdhMeinBerlinKiezkassenWorkbench = require("../Workbench/Workbench");

import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");

var pkgLocation = "/MeinBerlin/Kiezkassen/Context";


export var headerDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/header.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");
        }
    };

};


export var moduleName = "adhMeinBerlinKiezkassenContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhMeinBerlinKiezkassenWorkbench.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhKiezkassenContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkassen");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("kiezkassen", ["adhConfig", "$templateRequest", (
                    adhConfig : AdhConfig.IService,
                    $templateRequest : angular.ITemplateRequestService
                ) => {
                    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
                }]);
            AdhMeinBerlinKiezkassenWorkbench.registerRoutes(
                RIKiezkassenProcess.content_type,
                "kiezkassen"
            )(adhResourceAreaProvider);
        }]);
};
