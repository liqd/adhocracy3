import * as AdhConfig from "../Core/Config/Config";
import * as AdhHttp from "../Core/Http/Http";

import * as SIActivity from "../../../Resources_/adhocracy_core/sheets/activity/IActivity";
import * as SIPool from "../../../Resources_/adhocracy_core/sheets/pool/IPool";

var pkgLocation = "/Core/Activity";


export var streamDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Stream.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.$watch("path", (path) => {
                if (path) {
                    adhHttp.get(path, {elements: "paths"}).then((stream) => {
                        scope.elements = SIPool.get(stream).elements;
                    });
                }
            });
        }
    };
};


export var activityDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Activity.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.$watch("path", (path) => {
                if (path) {
                    adhHttp.get(path).then((stream) => {
                        scope.name = SIActivity.get(stream).name;
                    });
                }
            });
        }
    };
};
