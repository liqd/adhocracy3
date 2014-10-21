import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

import RIBasicPool = require("../../Resources_/adhocracy_core/resources/pool/IBasicPool");
import RIMercatorProposal = require("../../Resources_/adhocracy_core/resources/mercator/IMercatorProposal");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");

var notFoundTemplate = "<h1>404 - not Found</h1>";


export interface IResourceRouterScope extends ng.IScope {
    template : string;
}


export var resourceRouter = (
    adhHttp : AdhHttp.Service<any>,
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service,
    $routeParams : ng.route.IRouteParamsService,
    $scope : IResourceRouterScope
) => {
    var resourceUrl = adhConfig.rest_url + "/" + $routeParams["path"];

    adhHttp.get(resourceUrl).then((resource) => {
        switch (resource.content_type) {
            case RIBasicPool.content_type:
                $scope.template = "<adh-document-workbench></adh-document-workbench>";
                break;
            case RIMercatorProposal.content_type:
                $scope.template = "<adh-document-workbench></adh-document-workbench>";
                break;
            case RIUser.content_type:
                $scope.template = "<h1>User</h1>";
                break;
            case RIUsersService.content_type:
                $scope.template = "<h1>User List</h1>";
                break;
            default:
                $scope.template = notFoundTemplate;
        }
    }, (reason) => {
        $scope.template = notFoundTemplate;
    });
};


export var viewFactory = ($compile : ng.ICompileService) => {
    return {
        restrict: "E",
        scope: {
            template: "@"
        },
        link: (scope, element) => {
            scope.$watch("template", (template) => {
                element.html(template);
                $compile(element.contents())(scope);
            });
        }
    };
};
