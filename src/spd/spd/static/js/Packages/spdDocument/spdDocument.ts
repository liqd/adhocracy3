/* tslint:disable:variable-name */
/// <reference path="../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhInject = require("../Inject/Inject");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhPermissions = require("../Permissions/Permissions");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhRate = require("../Rate/Rate");
import AdhSticky = require("../Sticky/Sticky");
import AdhEmbed = require("../Embed/Embed");

var pkgLocation = "/spdDocument";

// FIXME: Can be removed when we work with real data
export var dummydata = [
    "## Hallo \n\n Lorem ipsum dolor sit amet, " +
     "consectetur adipiscing elit. Phasellus quis " +
     "lectus metus, at posuere neque. Sed pharetra " +
     "nibh eget orci convallis at posuere leo convallis. " +
     "Sed blandit augue vitae augue scelerisque bibendum. " +
     "Vivamus sit amet libero turpis, non venenatis urna. " +
     "In blandit, odio convallis suscipit venenatis, ante " +
     "ipsum cursus augue.",
     "## Toll \n\n Lorem ipsum dolor sit amet, " +
     "consectetur adipiscing elit. Phasellus quis " +
     "lectus metus, at posuere neque. Sed pharetra " +
     "nibh eget orci convallis at posuere leo convallis. " +
     "Sed blandit augue vitae augue scelerisque bibendum. " +
     "Vivamus sit amet libero turpis, non venenatis urna. " +
     "In blandit, odio convallis suscipit venenatis, ante " +
     "ipsum cursus augue.",
     "## Klasse! \n\n Lorem ipsum dolor sit amet," +
     "consectetur adipiscing elit. Phasellus quis " +
     "lectus metus, at posuere neque. Sed pharetra " +
     "nibh eget orci convallis at posuere leo convallis. " +
     "Sed blandit augue vitae augue scelerisque bibendum. " +
     "Vivamus sit amet libero turpis, non venenatis urna. " +
     "In blandit, odio convallis suscipit venenatis, ante " +
     "ipsum cursus augue."
];

export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {

        // FIXME: not final
        title : string;
        paragraphs : string[];
    };
    selectedState? : string;
    resource: any;
}

export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            scope.data = {
                title: "Toller Titel",
                paragraphs: dummydata
            };
        }
    };
};

export var listItemDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            console.log("here comes the stuff");
        }
    };
};

export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope, element) => {
            scope.errors = [];
            scope.data = {};
            scope.create = true;
            scope.showError = adhShowError;
        }
    };
};

export var editDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            console.log("here comes the stuff");
        }
    };
};

export var moduleName = "adhSPDDocument";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            "ngMessages",
            AdhAngularHelpers.moduleName,
            AdhHttp.moduleName,
            AdhInject.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhResourceArea.moduleName,
            AdhResourceWidgets.moduleName,
            AdhSticky.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("spd-document-detail");
            adhEmbedProvider.embeddableDirectives.push("spd-document-create");
            adhEmbedProvider.embeddableDirectives.push("spd-document-edit");
            adhEmbedProvider.embeddableDirectives.push("spd-document-list-item");
        }])
        .directive("adhSpdDocumentDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", detailDirective])
        .directive("adhSpdDocumentCreate", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhShowError", "adhSubmitIfValid", createDirective])
        .directive("adhSpdDocumentEdit", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", editDirective])
        .directive("adhSpdDocumentListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", listItemDirective]);
};
