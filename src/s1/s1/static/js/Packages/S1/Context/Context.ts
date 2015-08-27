import AdhConfig = require("../../Config/Config");
import AdhEmbed = require("../../Embed/Embed");
import AdhPermissions = require("../../Permissions/Permissions");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../TopLevelState/TopLevelState");
import AdhUserViews = require("../../User/Views");

import AdhS1Workbench = require("../Workbench/Workbench");

import RIS1Process = require("../../../Resources_/adhocracy_s1/resources/s1/IProcess");

var pkgLocation = "/S1/Context";


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
            scope.$on("$destroy", adhTopLevelState.bind("meeting", scope));
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");
        }
    };
};


export var moduleName = "adhS1Context";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhS1Workbench.moduleName,
            AdhTopLevelState.moduleName,
            AdhUserViews.moduleName
        ])
        .directive("adhS1ContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("s1");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("s1", ["adhConfig", "$templateRequest", (
                    adhConfig : AdhConfig.IService,
                    $templateRequest : angular.ITemplateRequestService
                ) => {
                    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
                }]);
            AdhS1Workbench.registerRoutes(RIS1Process.content_type, "s1")(adhResourceAreaProvider);
            AdhUserViews.registerRoutes("s1")(adhResourceAreaProvider);
        }]);
};
