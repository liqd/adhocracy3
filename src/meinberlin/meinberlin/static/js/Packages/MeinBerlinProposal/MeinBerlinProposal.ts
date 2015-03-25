import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");

var pkgLocation = "/MeinBerlinProposal";


export var createDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope, element, attrs) => {
            var data = {};
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
