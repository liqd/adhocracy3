import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");

import AdhMeinBerlinBurgerhaushaltWorkbench = require("../Workbench/Workbench");

import RIBurgerhaushaltProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess");

var pkgLocation = "/MeinBerlin/Burgerhaushalt/Context";


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


export var moduleName = "adhMeinBerlinBurgerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhMeinBerlinBurgerhaushaltWorkbench.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhBurgerhaushaltContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("burgerhaushalt");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("burgerhaushalt", ["adhConfig", "$templateRequest", (
                    adhConfig : AdhConfig.IService,
                    $templateRequest : angular.ITemplateRequestService
                ) => {
                    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
                }]);
            AdhMeinBerlinBurgerhaushaltWorkbench.registerRoutes(
                RIBurgerhaushaltProcess.content_type,
                "burgerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
