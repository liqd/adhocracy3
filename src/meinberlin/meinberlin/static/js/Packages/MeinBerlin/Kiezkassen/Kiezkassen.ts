import AdhMeinBerlinKiezkassenProposal = require("./Proposal/Proposal");

var pkgLocation = "/MeinBerlin/Kiezkassen";


export var detailDirective = (adhConfig : AdhConfig.IService, adhHttp : AdhHttp.Service<any>) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.currentTab = 0;

            scope.$watch(pathKey, (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        // FIXME: set individual fields on scope, not simply dump whole resource
                        scope.resource = resource;
                    });
                    adhHttp.options(value).then((options : AdhHttp.IOptions) => {
                        scope.options = options;
                    });
                }
            });
        }
    };
};


export var moduleName = "adhMeinBerlinKiezkassen";

export var register = (angular) => {
    AdhMeinBerlinKiezkassenProposal.register(angular);

    angular
        .module(moduleName, [
            AdhMeinBerlinKiezkassenProposal.moduleName
        ])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", detailDirective]);
};
