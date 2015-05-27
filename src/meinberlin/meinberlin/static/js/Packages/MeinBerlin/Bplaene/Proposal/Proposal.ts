/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAngularHelpers = require("../../../AngularHelpers/AngularHelpers");
import AdhEmbed = require("../../../Embed/Embed");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhConfig = require("../../../Config/Config");

var pkgLocation = "/MeinBerlin/Bplaene/Proposal";


export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            onSuccess: "=?"
        },
        link: (scope, element) => {
            scope.errors = [];
            scope.data = {};
            scope.showError = adhShowError;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    console.log("success");

                    if (typeof scope.onSuccess !== "undefined") {
                        scope.onSuccess();
                    }
                });
            };
        }
    };
};



export var moduleName = "adhMeinBplaeneProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhEmbed.moduleName,
            AdhResourceArea.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-bplaene-proposal-create");
        }])
        .directive("adhMeinBerlinBplaeneProposalCreate", ["adhConfig", "adhShowError", "adhSubmitIfValid", createDirective]);
};
