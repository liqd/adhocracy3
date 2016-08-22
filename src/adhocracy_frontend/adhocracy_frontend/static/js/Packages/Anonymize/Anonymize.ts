import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhUser from "../User/User";

var pkgLocation = "/Anonymize";


export var getAnonymizeOptional = (
    adhHttp : AdhHttp.Service
) => (
    url : string,
    method : string
) => {
    return adhHttp.options(url, {importOptions: false}).then((rawOptions) => {
        return (<any>rawOptions).data[method].request_headers.hasOwnProperty("X-Anonymize");
    });
};

export var anonymizeDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhUser : AdhUser.Service,
    $q : angular.IQService
) => {
    var _getAnonymizeOptional = getAnonymizeOptional(adhHttp);

    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Anonymize.html",
        scope: {
            url: "@",
            method: "@",
            model: "=",
        },
        link: (scope) => {
            scope.isEnabled = adhConfig.anonymize_enabled;

            if (scope.isEnabled) {
                scope.data = {};
                scope.data.model = false;
                scope.isOptional = false;

                $q.all([
                    adhUser.ready,
                    _getAnonymizeOptional(scope.url, scope.method)
                ]).then((args) => {
                    scope.isOptional = args[1];
                    scope.data.model = scope.isOptional ? adhUser.data.anonymize : false;
                });

                scope.$watch("data.model", (model) => {
                    scope.model = model;
                });
            }
        }
    };
};
