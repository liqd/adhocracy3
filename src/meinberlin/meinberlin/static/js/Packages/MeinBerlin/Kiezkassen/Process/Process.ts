import AdhConfig = require("..././../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhTabs = require("../../../Tabs/Tabs");

import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");

var pkgLocation = "/MeinBerlin/Kiezkassen/Process";


export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.$watch(() => column.$scope.shared.isShowMap, (value : boolean) => {
                scope.showMap = value;
            });
            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        var locationUrl = resource.data[SILocationReference.nick].location;

                        adhHttp.get(locationUrl).then((location) => {
                            var polygon = location.data[SIMultiPolygon.nick].coordinates[0][0];
                            scope.polygon =  polygon;
                        });
                    });
                }
            });
            adhPermissions.bindScope(scope, () => scope.path);
        }
    };
};


export var moduleName = "adhMeinBerlinKiezkassenProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhTabs.moduleName
        ])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", "adhPermissions", detailDirective]);
};
