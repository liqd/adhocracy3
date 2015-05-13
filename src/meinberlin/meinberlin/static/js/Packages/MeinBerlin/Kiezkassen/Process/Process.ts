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
    adhPermissions : AdhPermissions.Service,
    $rootScope
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.shared = column.$scope.shared;
            scope.showMap = (isShowMap : boolean) => {
                scope.shared.isShowMap = isShowMap;
            };
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


export var phaseHeaderDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/PhaseHeader.html",
        scope: {},
        link: (scope) => {
            scope.phases = [{
                title: "Informationsphase",
                description: "Lorem ipsum Veniam deserunt nostrud aliquip officia aliqua esse Ut voluptate in consequat dolor.",
                processType: "Kiezkasse",
                startDate: "2015-01-01",
                endDate: "2015-02-02",
                votingAvailable: false,
                commentAvailable: false
            }, {
                title: "Ideensammlungsphase",
                description: "Alle Interessierten werden aufgerufen Vorschläge für Projekte in der Bezirksregion zu machen. " +
                    "Die Angabe der Kosten soll bitte die Mehrwertsteuer enthalten. Vorschläge können aber auch noch offline " +
                    "in der den. Alle Vorschläge (offline und online) werden dann bei der Bürgerversammlung beschlossen.",
                processType: "Kiezkasse",
                startDate: "2015-02-02",
                endDate: "2015-05-10",
                votingAvailable: true,
                commentAvailable: true
            }, {
                title: "Bürgerversammlung",
                description: "In dieser Phase können keine Vorschläge mehr online eingereicht, kommentiert oder bewertet " +
                    "werden. Vorschläge können aber noch offline in der Bürgerversammlung gemacht werden. Alle Vorschläge " +
                    "werden dann vor Ort die Art und Weise der Abstimmung bestimmt die Bürgerversammlung selbst. Offline " +
                    "Vorschläge werden online",
                processType: "Kiezkasse",
                startDate: "2015-05-10",
                endDate: "2015-05-20",
                votingAvailable: true,
                commentAvailable: false
            }, {
                title: "Ergebnisse",
                description: "Nach der Prüfung vom zuständigen Fachamt des Bezirksamtes werden die Vorschläge, die realisiert " +
                    "werden und ggf. diejenigen, die nicht realisierbar sind, online markiert und angezeigt. Die Projekte " +
                    "müssen bis Mitte Dezember realisiert und abgerechnet werden",
                processType: "Kiezkasse",
                startDate: "2015-05-20",
                votingAvailable: false,
                commentAvailable: false
            }];
        }
    };
};


export var phaseDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Phase.html",
        scope: {
            phase: "="
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
        .directive("adhMeinBerlinKiezkassenPhase", ["adhConfig", phaseDirective])
        .directive("adhMeinBerlinKiezkassenPhaseHeader", ["adhConfig", phaseHeaderDirective])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", "adhPermissions", "$rootScope", detailDirective]);
};
