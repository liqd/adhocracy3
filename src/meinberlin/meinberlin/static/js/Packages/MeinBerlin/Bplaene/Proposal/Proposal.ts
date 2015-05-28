/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAngularHelpers = require("../../../AngularHelpers/AngularHelpers");
import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhHttp = require("../../../Http/Http");
import AdhUtil = require("../../../Util/Util");
import AdhPreliminaryNames = require("../../../PreliminaryNames/PreliminaryNames");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");

import RIProposal = require("../../../../Resources_/adhocracy_meinberlin/resources/bplan/IProposal");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/bplan/IProposalVersion");
import SIName = require("../../../../Resources_/adhocracy_core/sheets/name/IName");
import SIProposal = require("../../../../Resources_/adhocracy_meinberlin/sheets/bplan/IProposal");
import SIVersionable = require("../../../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/MeinBerlin/Bplaene/Proposal";


interface IScope extends angular.IScope {
    path : string;
    data : {
        name : string;
        street : string;
        city : string;
        email : string;
        statement : string;
    };
    errors : any[];
    showError : Function;
    onSuccess? : Function;
    submit() : void;
    meinBerlinProposalForm : any;
}


var postCreate = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    poolPath : string
) => {
    var proposal = new RIProposal({preliminaryNames: adhPreliminaryNames});
    proposal.parent = poolPath;
    // FIXME: dummy name
    proposal.data[SIName.nick] = new SIName.Sheet({
        name: AdhUtil.normalizeName(scope.data.name)
    });

    var proposalVersion = new RIProposalVersion({preliminaryNames: adhPreliminaryNames});
    proposalVersion.parent = proposal.path;
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [proposal.first_version_path]
    });
    proposalVersion.data[SIProposal.nick] = new SIProposal.Sheet({
        name: scope.data.name,
        street_number: scope.data.street,
        postal_code_city: scope.data.city,
        email: scope.data.email,
        statement: scope.data.statement
    });

    return adhHttp.deepPost([proposal, proposalVersion]);
};


export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@",
            onSuccess: "=?"
        },
        link: (scope : IScope, element) => {
            scope.errors = [];
            scope.data = {
                name: "",
                street: "",
                city: "",
                email: "",
                statement: ""
            };
            scope.showError = adhShowError;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path);

                    if (typeof scope.onSuccess !== "undefined") {
                        scope.onSuccess();
                    }
                });
            };
        }
    };
};


export var embedDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Embed.html",
        scope: {},
        link: (scope) => {
            scope.success = false;

            scope.showSuccess = () => {
                scope.success = true;
            };
            scope.showForm = () => {
                scope.success = false;
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
            AdhHttp.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhResourceArea.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-bplaene-proposal-embed");
        }])
        .directive("adhMeinBerlinBplaeneProposalCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", createDirective])
        .directive("adhMeinBerlinBplaeneProposalEmbed", ["adhConfig", embedDirective]);
};
