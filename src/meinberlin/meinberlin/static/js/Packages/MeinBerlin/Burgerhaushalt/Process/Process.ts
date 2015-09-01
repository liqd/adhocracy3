import AdhConfig = require("..././../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhProcess = require("../../../Process/Process");

import AdhMeinBerlinPhase = require("../../Phase/Phase");

import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");
import SIWorkflow = require("../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment");

var pkgLocation = "/MeinBerlin/Burgerhaushalt/Process";


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
            scope.shared = column.$scope.shared;
            scope.showMap = (isShowMap : boolean) => {
                scope.shared.isShowMap = isShowMap;
            };
            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        var sheet = resource.data[SIWorkflow.nick];
                        var stateName = sheet.workflow_state;
                        scope.currentPhase = AdhProcess.getStateData(sheet, stateName);

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


export var phaseHeaderDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + AdhMeinBerlinPhase.pkgLocation + "/PhaseHeader.html",
        scope: {},
        link: (scope : AdhMeinBerlinPhase.IPhaseHeaderScope) => {
            scope.phases = [{
                name: "information",
                title: "Information",
                description: "Ab dem 02.09.2015 können sich alle interessierten Bürgerinnen und Bürger zum Bürgerhaushalt " +
                    "Treptow-Köpenick online beteiligen. Auf der Internetseite des Bezirksamtes Treptow-Köpenick sowie eine " +
                    "Einwohnerversammlung werden allen Interessierten Informationen zum Verfahren zur Verfügung gestellt. Bisher " +
                    "offline eingereichte Vorschläge werden von den Fachämtern online eingetragen.",
                processType: "Bürgerhaushalt",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "collection",
                title: "Ideensammlung",
                description: "In dieser Phase bringen Bürgerinnen und Bürger ihre Vorschläge ein und können Vorschläge anderer bewerten " +
                    "und diskutieren. Vorschläge beziehen sich auf das laufende oder zukünftige Kalenderjahr und können stets " +
                    "eingebracht werden. Vorschläge können auch offline eingereicht werden.",
                processType: "Bürgerhaushalt",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "result",
                title: "Ergebnisse",
                description: "Bürgerinnen und Bürger können den Status aller Vorschläge sehen und gegebenenfalls die Stellungnahme des " +
                    "im Bezirksamt zuständigen Fachamtes lesen.",
                processType: "Bürgerhaushalt",
                votingAvailable: false,
                commentAvailable: false
            }];
        }
    };
};


export var moduleName = "adhMeinBerlinBurgerhaushaltProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhMeinBerlinPhase.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName
        ])
        .directive("adhMeinBerlinBurgerhaushaltPhaseHeader", ["adhConfig", phaseHeaderDirective])
        .directive("adhMeinBerlinBurgerhaushaltDetail", ["adhConfig", "adhHttp", "adhPermissions", detailDirective]);
};
