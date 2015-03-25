import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");

var pkgLocation = "/MeinBerlinProposal";


export var createDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope, element, attrs) => {
            scope.data = {};

            // FIXME: These values have to come from somewhere
            scope.data.lat = 52.5011278698;
            scope.data.lng = 13.3592486393;
        }
    };
};

export var meinBerlinProposalFormController = ($scope, $element, $window) => {
    console.log($scope);
};


export var moduleName = "adhMeinBerlinProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-create");
        }])
        .directive("adhMeinBerlinCreate", ["adhConfig", createDirective])
        .controller("meinBerlinProposalFormController", [meinBerlinProposalFormController]);
};
