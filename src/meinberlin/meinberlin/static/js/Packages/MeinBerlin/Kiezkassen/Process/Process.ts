/// <reference path="../../../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>
/// <reference path="../../../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

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


export var detailAnnounceDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DetailAnnounce.html",
        scope: {
            path: "@"
        },
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        scope.currentPhase = resource.data[SIKiezkassenWorkflow.nick].workflow_state;
                        scope.announceDescription = resource.data[SIKiezkassenWorkflow.nick].announce.description;
                    });
                }
            });
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
                title: "Information",
                description: "Mit den Kiezkassen können Projekte vor Ort unterstützt werden und sollen das " +
                "bürgerschaftliche Engagement fördern. Alle interessierte Bürger*innen können ab sofort sich " +
                "beteiligen und Vorschläge einreichen. Die Bürgerversammlung findet am 04. Juni 2015 um 19 Uhr in der " +
                "Nachbarschaftsgalerie der KungerKiez-Initiative e.V.. Karl-Kuhger- Straße 15, 12435 Berlin.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }, {
                name: "participate",
                title: "Ideensammlung",
                description: "Alle Interessierten werden aufgerufen Vorschläge für Projekte in der Bezirksregion " +
                "zu machen. Die Angabe der Kosten soll bitte die Mehrwertsteuer enthalten. Vorschläge können aber " +
                "auch noch offline in der Bürgerversammlung gemacht werden. Alle Vorschläge (offline und online) " +
                "werden dann bei der Bürgerversammlung beschlossen.",
                processType: "Kiezkasse",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "frozen",
                title: "Bürgerversammlung",
                description: "In dieser Phase können keine Vorschläge mehr online eingereicht, kommentiert oder " +
                "bewertet werden. Vorschläge können aber noch offline in der Bürgerversammlung gemacht werden. Alle " +
                "Vorschläge werden dann vor Ort vorgestellt und abgestimmt. Die Art und Weise der Abstimmung bestimmt " +
                "die Bürgerversammlung selbst. Offline Vorschläge werden online eingereicht.",
                processType: "Kiezkasse",
                votingAvailable: false,
                commentAvailable: false
            }, {
                name: "result",
                title: "Ergebnisse",
                description: "Nach der Prüfung vom zuständigen Fachamt des Bezirksamtes werden die Vorschläge, die " +
                "realisiert werden und ggf. diejenigen, die nicht realisierbar sind, online markiert und angezeigt. " +
                "Die Projekte müssen bis Mitte Dezember realisiert und abgerechnet werden.",
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
    adhSubmitIfValid,
    moment
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

                scope.data.announce_description = process.data[SIKiezkassenWorkflow.nick].announce.description;
                scope.data.announce_start_date = moment(process.data[SIKiezkassenWorkflow.nick].announce.start_date).format("YYYY-MM-DD");

                scope.data.draft_description = process.data[SIKiezkassenWorkflow.nick].draft.description;
                scope.data.draft_start_date = moment(process.data[SIKiezkassenWorkflow.nick].draft.start_date).format("YYYY-MM-DD");

                scope.data.participate_description = process.data[SIKiezkassenWorkflow.nick].participate.description;
                scope.data.participate_start_date = moment(
                                                            process.data[SIKiezkassenWorkflow.nick]
                                                            .participate.start_date
                                                           ).format("YYYY-MM-DD");

                scope.data.frozen_description = process.data[SIKiezkassenWorkflow.nick].frozen.description;
                scope.data.frozen_start_date = moment(process.data[SIKiezkassenWorkflow.nick].frozen.start_date).format("YYYY-MM-DD");

                scope.data.result_description = process.data[SIKiezkassenWorkflow.nick].result.description;
                scope.data.result_start_date = moment(process.data[SIKiezkassenWorkflow.nick].result.start_date).format("YYYY-MM-DD");

                scope.data.currentWorkflowState = process.data[SIKiezkassenWorkflow.nick].workflow_state;
            });
            adhHttp.options(scope.path, {importOptions: false}).then((raw) => {
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
                        process.data[SIKiezkassenWorkflow.nick] = {
                            workflow_state: scope.data.currentWorkflowState
                        };
                    }

                    process.data[SIKiezkassenWorkflow.nick]["announce"] = {};
                    process.data[SIKiezkassenWorkflow.nick]["announce"].description = scope.data.announce_description;
                    process.data[SIKiezkassenWorkflow.nick]["announce"].start_date = scope.data.announce_start_date;

                    process.data[SIKiezkassenWorkflow.nick]["draft"] = {};
                    process.data[SIKiezkassenWorkflow.nick]["draft"].description = scope.data.draft_description;
                    process.data[SIKiezkassenWorkflow.nick]["draft"].start_date = scope.data.draft_start_date;

                    process.data[SIKiezkassenWorkflow.nick]["participate"] = {};
                    process.data[SIKiezkassenWorkflow.nick]["participate"].description = scope.data.participate_description;
                    process.data[SIKiezkassenWorkflow.nick]["participate"].start_date = scope.data.participate_start_date;

                    process.data[SIKiezkassenWorkflow.nick]["frozen"] = {};
                    process.data[SIKiezkassenWorkflow.nick]["frozen"].description = scope.data.frozen_description;
                    process.data[SIKiezkassenWorkflow.nick]["frozen"].start_date = scope.data.frozen_start_date;

                    process.data[SIKiezkassenWorkflow.nick]["result"] = {};
                    process.data[SIKiezkassenWorkflow.nick]["result"].description = scope.data.result_description;
                    process.data[SIKiezkassenWorkflow.nick]["result"].start_date = scope.data.result_start_date;

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
            AdhTabs.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhMeinBerlinKiezkassenPhase", ["adhConfig", phaseDirective])
        .directive("adhMeinBerlinKiezkassenPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", phaseHeaderDirective])
        .directive("adhMeinBerlinKiezkassenDetail", ["adhConfig", "adhHttp", "adhPermissions", detailDirective])
        .directive("adhMeinBerlinKiezkassenDetailAnnounce", ["adhConfig", "adhHttp", detailAnnounceDirective])
        .directive("adhMeinBerlinKiezkassenEdit", ["adhConfig", "adhHttp", "adhSubmitIfValid", "moment", editDirective]);
};
