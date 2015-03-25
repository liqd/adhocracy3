import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");

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
            AdhEmbed.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-create");
        }])
        .directive("adhMeinBerlinCreate", [createDirective])
        .controller("meinBerlinProposalFormController", [meinBerlinProposalFormController]);
};
