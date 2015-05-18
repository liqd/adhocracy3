/// <reference path="../../../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("..././../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhTabs = require("../../../Tabs/Tabs");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUtil = require("../../../Util/Util");

import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");
import SITitle = require("../../../../Resources_/adhocracy_core/sheets/title/ITitle");

import SIKiezkassenWorkflow = require("../../../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IWorkflowAssignment");

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
            scope.shared = column.$scope.shared;
            scope.showMap = (isShowMap : boolean) => {
                scope.shared.isShowMap = isShowMap;
            };
            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        scope.currentPhase = resource.data[SIKiezkassenWorkflow.nick].workflow_state;
                        scope.announceDescription = resource.data[SIKiezkassenWorkflow.nick].announce.description;

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
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/PhaseHeader.html",
        scope: {},
        link: (scope) => {
            var processUrl = adhTopLevelState.get("processUrl");
            adhHttp.get(processUrl).then((resource) => {
                scope.currentPhase = resource.data[SIKiezkassenWorkflow.nick].workflow_state;
                scope.phases[0].startDate = resource.data[SIKiezkassenWorkflow.nick].announce.start_date;
                scope.phases[0].endDate = resource.data[SIKiezkassenWorkflow.nick].participate.start_date;
                scope.phases[1].startDate = resource.data[SIKiezkassenWorkflow.nick].participate.start_date;
                scope.phases[1].endDate = resource.data[SIKiezkassenWorkflow.nick].frozen.start_date;
                scope.phases[2].startDate = resource.data[SIKiezkassenWorkflow.nick].frozen.start_date;
                scope.phases[2].endDate = resource.data[SIKiezkassenWorkflow.nick].result.start_date;
                scope.phases[3].startDate = resource.data[SIKiezkassenWorkflow.nick].result.start_date;
            });

            // FIXME: dummy content
            scope.phases = [{
                name: "announce",
                title: "Informationsphase",
                description: "Lorem ipsum Veniam deserunt nostrud aliquip officia aliqua esse Ut voluptate in consequat dolor.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }, {
                name: "participate",
                title: "Ideensammlungsphase",
                description: "Alle Interessierten werden aufgerufen Vorschläge für Projekte in der Bezirksregion zu machen. " +
                    "Die Angabe der Kosten soll bitte die Mehrwertsteuer enthalten. Vorschläge können aber auch noch offline " +
                    "in der den. Alle Vorschläge (offline und online) werden dann bei der Bürgerversammlung beschlossen.",
                processType: "Kiezkasse",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "frozen",
                title: "Bürgerversammlung",
                description: "In dieser Phase können keine Vorschläge mehr online eingereicht, kommentiert oder bewertet " +
                    "werden. Vorschläge können aber noch offline in der Bürgerversammlung gemacht werden. Alle Vorschläge " +
                    "werden dann vor Ort die Art und Weise der Abstimmung bestimmt die Bürgerversammlung selbst. Offline " +
                    "Vorschläge werden online",
                processType: "Kiezkasse",
                votingAvailable: true,
                commentAvailable: false
            }, {
                name: "result",
                title: "Ergebnisse",
                description: "Nach der Prüfung vom zuständigen Fachamt des Bezirksamtes werden die Vorschläge, die realisiert " +
                    "werden und ggf. diejenigen, die nicht realisierbar sind, online markiert und angezeigt. Die Projekte " +
                    "müssen bis Mitte Dezember realisiert und abgerechnet werden",
                processType: "Kiezkasse",
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


export var editDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Edit.html",
        scope: {
            path: "@"
        },
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            var process;
            scope.data = {};
            adhHttp.get(scope.path).then((resource) => {
                process = resource;
                scope.data.title = process.data[SITitle.nick].title;
                scope.data.currentWorkflowState = process.data[SIKiezkassenWorkflow.nick].workflow_state;
            });
            adhHttp.options(scope.path, false).then((raw) => {
                // extract available transitions
                scope.data.availableWorkflowStates = AdhUtil.deepPluck(raw, [
                    "data", "PUT", "request_body", "data", SIKiezkassenWorkflow.nick, "workflow_state"]);
            });
            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.kiezkassenProcessForm, () => {
                    process.data[SITitle.nick].title = scope.data.title;
                    process.data["adhocracy_core.sheets.name.IName"] = undefined;
                    process.data["adhocracy_core.sheets.image.IImageReference"] = undefined;
                    if (_.contains(scope.data.availableWorkflowStates, scope.data.workflowState)) {
                        process.data[SIKiezkassenWorkflow.nick] = {
                            workflow_state: scope.data.workflowState
                        };
                    } else {
                        process.data[SIKiezkassenWorkflow.nick] = undefined;
                    }

                    return adhHttp.put(process.path, process);
                });
            };
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
        .directive("adhMeinBerlinKiezkassenPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", phaseHeaderDirective])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", "adhPermissions", detailDirective])
        .directive("adhMeinBerlinKiezkassenEdit", ["adhConfig", "adhHttp", "adhSubmitIfValid", editDirective]);
};
