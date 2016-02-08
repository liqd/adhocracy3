import * as AdhConfig from "../../../Config/Config";
import * as AdhHttp from "../../../Http/Http";
import * as AdhTopLevelState from "../../../TopLevelState/TopLevelState";

import * as AdhMeinberlinPhase from "../../Phase/Phase";


export var phaseHeaderDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + AdhMeinberlinPhase.pkgLocation + "/PhaseHeader.html",
        scope: {},
        link: (scope : AdhMeinberlinPhase.IPhaseHeaderScope) => {
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
                    "geht es um die Arbeit am neuen Masterplan. Zwischenergebnisse und Vorschläge erweitern die Ausstellung im " +
                    "Alexanderhaus. Die Anmerkungen aus der Onlinebeteiligung werden in die Workshops mit einfließen.",
                processType: "Workshopverfahren Alexanderplatz",
                votingAvailable: false,
                commentAvailable: false
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
