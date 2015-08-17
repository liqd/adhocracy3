import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhHttp = require("../../../Http/Http");
import AdhMapping = require("../../../Mapping/Mapping");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");

import AdhMeinBerlinAlexanderplatzWorkbench = require("../Workbench/Workbench");

import RIAlexanderplatzProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess");
import RIGeoDocument = require("../../../../Resources_/adhocracy_core/resources/document/IGeoDocument");
import RIGeoDocumentVersion = require("../../../../Resources_/adhocracy_core/resources/document/IGeoDocumentVersion");
import RIGeoProposal = require("../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposal");
import RIGeoProposalVersion = require("../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion");
import RIParagraph = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIParagraph = require("../../../../Resources_/adhocracy_core/sheets/document/IParagraph");

var pkgLocation = "/MeinBerlin/Alexanderplatz/Context";


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
            scope.proposalItemType = RIGeoProposal.content_type;

            scope.setCameFrom = () => {
                adhTopLevelState.setCameFrom();
            };
        }
    };

};


export var moduleName = "adhMeinBerlinAlexanderplatzContext";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhHttp.moduleName,
            AdhMeinBerlinAlexanderplatzWorkbench.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhAlexanderplatzContextHeader", ["adhConfig", "adhPermissions", "adhTopLevelState", headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("alexanderplatz");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider: AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("alexanderplatz", ["adhConfig", "$templateRequest", (
                    adhConfig: AdhConfig.IService,
                    $templateRequest: angular.ITemplateRequestService
                    ) => {
                    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
                }]);
            AdhMeinBerlinAlexanderplatzWorkbench.registerRoutes(processType, "alexanderplatz")(adhResourceAreaProvider);
        }])
        .config(["adhMapDataProvider", (adhMapDataProvider: AdhMapping.MapDataProvider) => {
            adhMapDataProvider.icons["document"] = {
                className: "icon-board-pin",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
            adhMapDataProvider.icons["document-selected"] = {
                className: "icon-board-pin is-active",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
        }]);
};
