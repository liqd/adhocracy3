import AdhConfig = require("../Config/Config");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

export var createDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: "/static/js/Packages/MeinBerlinProposal/Create.html",
        link: (scope, element, attrs) => {
            var data = {};
        }
    };
};

export var moduleName = "adhMeinBerlinProposal";

export var meinBerlinProposalFormController = ($scope, $element, $window) => {
    console.log($scope);
};

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        // FIXME: This will probably require proper routing
        .config(["adhEmbedProvider", (adhEmbedProvider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-create");
        }])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("mein_berlin_create", () : AdhTopLevelState.IAreaInput => {
                    return {
                        template: "<adh-mein-berlin-create></adh-mein-berlin-create>"
                    };
                });
        }])
        .directive("adhMeinBerlinCreate", [createDirective])
        .controller("meinBerlinProposalFormController", [meinBerlinProposalFormController]);
};
