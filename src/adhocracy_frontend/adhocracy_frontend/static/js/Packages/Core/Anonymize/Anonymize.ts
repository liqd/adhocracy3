import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhUser from "../User/User";

var pkgLocation = "/Core/Anonymize";


export interface IAnonymizeInfo {
    isEnabled : boolean;
    isOptional : boolean;
    defaultValue : boolean;
}

export var getAnonymizeInfo = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhUser : AdhUser.Service,
    $q : angular.IQService
) => (
    url : string,
    method : string,
    localDefault? : boolean
) : angular.IPromise<IAnonymizeInfo> => {
    var info : IAnonymizeInfo = {
        isEnabled: adhConfig.anonymize_enabled,
        isOptional: false,
        defaultValue: false,
    };

    if (info.isEnabled) {
        var getOptional = (url, method) => {
            return adhHttp.options(url, {importOptions: false}).then((rawOptions) => {
                return (<any>rawOptions).data[method].request_headers.hasOwnProperty("X-Anonymize");
            });
        };

        return $q.all([
            adhUser.ready,
            getOptional(url, method),
        ]).then((args) => {
            info.isOptional = <boolean>args[1];
            var def = typeof localDefault === "undefined" ? adhUser.data.anonymize : localDefault;
            info.defaultValue = info.isOptional ? def : false;
            return info;
        });
    } else {
        return $q.when(info);
    }
};

export var anonymizeDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhUser : AdhUser.Service,
    $q : angular.IQService
) => {
    var _getAnonymizeInfo = getAnonymizeInfo(adhConfig, adhHttp, adhUser, $q);

    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Anonymize.html",
        scope: {
            url: "@",
            method: "@",
            localDefault: "=?",
            model: "=",
        },
        link: (scope) => {
            // already set values so they show up as inactive if isEnabled
            scope.isEnabled = adhConfig.anonymize_enabled;
            scope.isOptional = false;
            scope.data = {};

            if (scope.isEnabled) {
                scope.$watch("data.model", (model) => {
                    scope.model = model;
                });

                _getAnonymizeInfo(scope.url, scope.method, scope.localDefault).then((info : IAnonymizeInfo) => {
                    scope.isEnabled = info.isEnabled;
                    scope.isOptional = info.isOptional;
                    scope.data.model = info.defaultValue;
                });
            }
        }
    };
};
