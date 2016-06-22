import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhMovingColumns from "../MovingColumns/MovingColumns";

var pkgLocation = "/Abuse";


export var reportAbuseDirective = (adhHttp : AdhHttp.Service<any>, adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Abuse.html",
        scope: {
            url: "@",  // frontend URL
            modals: "=",
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.netiquette_url = adhConfig.netiquette_url;
            scope.submit = () => {
                return adhHttp.postRaw(adhConfig.rest_url + "/report_abuse", {
                    url: scope.url,
                    remark: scope.remark
                }).then(() => {
                    scope.modals.hideOverlay("abuse");
                    scope.modals.alert("TR__REPORT_ABUSE_STATUS_OK", "success");
                }, () => {
                    // FIXME
                });
            };

            scope.cancel = () => {
                scope.modals.hideOverlay("abuse");
            };
        }
    };
};

