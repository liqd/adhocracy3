/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhComment = require("../Comment/Comment");
import AdhConfig = require("../Config/Config");
import AdhListing = require("../Listing/Listing");
import AdhMercatorProposal = require("../MercatorProposal/MercatorProposal");
import AdhUser = require("../User/User");

import RIMercatorProposalVersion = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposalVersion");

var pkgLocation = "/MercatorWorkbench";

interface IMercatorWorkbenchScope extends ng.IScope {
    path : string;
    user : AdhUser.Service;
    websocketTestPaths : string;
    contentType : string;
    facets : AdhListing.IFacet[];
}

export class MercatorWorkbench {
    public static templateUrl : string = pkgLocation + "/MercatorWorkbench.html";

    public createDirective(adhConfig : AdhConfig.IService) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + _class.templateUrl,
            controller: ["adhUser", "$scope", (
                adhUser : AdhUser.Service,
                $scope : IMercatorWorkbenchScope
            ) : void => {
                $scope.path = adhConfig.rest_url + adhConfig.custom["mercator_platform_path"];
                $scope.contentType = RIMercatorProposalVersion.content_type;
                $scope.user = adhUser;
                $scope.websocketTestPaths = JSON.stringify([$scope.path]);
                $scope.facets = [
                    {
                        key: "mercator_location",
                        name: "Location",
                        items: [
                            {key: "specific", name: "Specific"},
                            {key: "online", name: "Online"},
                            {key: "linked_to_ruhr", name: "Linked to the Ruhr area"}
                        ]
                    },
                    {
                        key: "mercator_budget",
                        name: "Budget",
                        items: [
                            {key: "5000", name: "0 - 5000 €"},
                            {key: "10000", name: "5000 - 10000 €"},
                            {key: "20000", name: "10000 - 20000 €"},
                            {key: "50000", name: "20000 - 50000 €"}
                        ]
                    }
                ];
            }]
        };
    }
}


export var moduleName = "adhMercatorWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhComment.moduleName,
            AdhMercatorProposal.moduleName,
            AdhUser.moduleName
        ])
        .directive("adhMercatorWorkbench", ["adhConfig", (adhConfig) =>
            new MercatorWorkbench().createDirective(adhConfig)]);
};
