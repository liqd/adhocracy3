import AdhConfig = require("..././../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhTabs = require("../../../Tabs/Tabs");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");

import SIWorkflow = require("../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment");

var pkgLocation = "/MeinBerlin/Alexanderplatz/Process";


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

            scope.currentPhase = adhConfig.custom["alexanderplatz_phase"];

            scope.phases = [{
                name: "participate",
                shorttitle: "Phase 1",
                title: "Veränderungsstrategien für den neuen Masterplan.",
                description: "Was bleibt wie es ist und was muss und kann geändert werden (thematisch und räumlich) " +
                    "am Masterplan für den Alexanderplatz? Die Auswertung des 1. Fachworkshops sowie Anmerkungen aus " +
                    "der Onlinebeteiligung fließen in den Bürgerworkshop am 01.09 ein. In den Workshops, in der begleitenden " +
                    "Ausstellung am Alexanderplatz (20.08. – 06.09., Alexanderhaus - Eingang Dircksenstraße) " +
                    "sowie hier online wird zusammengetragen und diskutiert.",
                processType: "Workshopverfahren Alexanderplatz",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "evaluate",
                shorttitle: "Phase 2",
                title: "Varianten und Alternativen für den neuen Masterplan.",
                description: "November bis Dezember 2015. Im zweiten Fachworkshop am 02.11. und im zweiten Bürgerworkshop am 09.11. " +
                    "geht es um die Arbeit am neuen Masterplan. Zwischenergebnisse und Vorschläge erweitern die Ausstellung im Alexanderhaus. " +
                    "Die Anmerkungen aus der Onlinebeteiligung werden in die Workshops mit einfließen.",
                processType: "Workshopverfahren Alexanderplatz",
                votingAvailable: true,
                commentAvailable: true
            }, {
                name: "result",
                shorttitle: "Phase 3",
                title: "Der neue Masterplan wird vorgestellt.",
                description: "Aus den Ergebnissen der Workshops, der Onlinebeteiligung sowie Anregungen aus der Ausstellung wird ein " +
                    "neuer Masterplan zum Beschluss für das Abgeordnetenhaus entwickelt. Voraussichtlich im Frühjahr 2016 gibt es eine " +
                    "Finissage/Abschlussausstellung.",
                processType: "Workshopverfahren Alexanderplatz",
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

export var moduleName = "adhMeinBerlinAlexanderplatzProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhTabs.moduleName,
            AdhTopLevelState.moduleName
        ])
        .directive("adhMeinBerlinAlexanderplatzPhase", ["adhConfig", phaseDirective])
        .directive("adhMeinBerlinAlexanderplatzPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", phaseHeaderDirective]);
};
