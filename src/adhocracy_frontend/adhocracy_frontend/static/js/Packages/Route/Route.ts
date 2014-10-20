import AdhHttp = require("../Http/Http");
import AdhConfig = require("../Config/Config");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

var notFoundTemplate = "<h1>404 - not Found</h1>";


interface IResourceRouterScope extends ng.IScope {
    template : string;
}


export var resourceRouter = (
    adhHttp : AdhHttp.Service<any>,
    adhConfig : AdhConfig.Type,
    adhTopLevelState : AdhTopLevelState.TopLevelState,
    $routeParams : ng.route.IRouteParamsService,
    $scope : IResourceRouterScope
) => {
    var resourceUrl = adhConfig.rest_url + "/" + $routeParams["path"];

    adhHttp.get(resourceUrl).then((resource) => {
        switch (resource.content_type) {
            case "adhocracy_core.resources.sample_proposal.IProposal":
                $scope.template = "<adh-document-workbench></adh-document-workbench>";
                break;
            default:
                $scope.template = notFoundTemplate;
        }
    }, (reason) => {
        $scope.template = notFoundTemplate;
    });
};
