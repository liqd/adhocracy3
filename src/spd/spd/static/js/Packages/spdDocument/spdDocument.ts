/* tslint:disable:variable-name */
/// <reference path="../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhImage = require("../Image/Image");
import AdhInject = require("../Inject/Inject");
import AdhPermissions = require("../Permissions/Permissions");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhRate = require("../Rate/Rate");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhSticky = require("../Sticky/Sticky");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/spdDocument";

// FIXME: Can be removed when we work with real data
export var dummydata : IParagraph[] = [{
    body: "## Hallo \n\n Lorem ipsum dolor sit amet, " +
        "consectetur adipiscing elit. Phasellus quis " +
        "lectus metus, at posuere neque. Sed pharetra " +
        "nibh eget orci convallis at posuere leo convallis. " +
        "Sed blandit augue vitae augue scelerisque bibendum. " +
        "Vivamus sit amet libero turpis, non venenatis urna. " +
        "In blandit, odio convallis suscipit venenatis, ante " +
        "ipsum cursus augue.",
    commentCount: 5,
    path: "/adhocracy/Toller_Titel/PARAGRAPH_0000001/VERSION_0000001"
}, {
     body: "## Toll \n\n Lorem ipsum dolor sit amet, " +
        "consectetur adipiscing elit. Phasellus quis " +
        "lectus metus, at posuere neque. Sed pharetra " +
        "nibh eget orci convallis at posuere leo convallis. " +
        "Sed blandit augue vitae augue scelerisque bibendum. " +
        "Vivamus sit amet libero turpis, non venenatis urna. " +
        "In blandit, odio convallis suscipit venenatis, ante " +
        "ipsum cursus augue."
}, {
     body: "## Klasse! \n\n Lorem ipsum dolor sit amet," +
        "consectetur adipiscing elit. Phasellus quis " +
        "lectus metus, at posuere neque. Sed pharetra " +
        "nibh eget orci convallis at posuere leo convallis. " +
        "Sed blandit augue vitae augue scelerisque bibendum. " +
        "Vivamus sit amet libero turpis, non venenatis urna. " +
        "In blandit, odio convallis suscipit venenatis, ante " +
        "ipsum cursus augue."
}];

export interface IParagraph {
    body : string;
    commentCount? : number;
    path? : string;
}

export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {
        title : string;
        paragraphs? : IParagraph[];
        commentCountTotal? : number;
        picture? : string;
    };
    selectedState? : string;
    resource: any;
}

export interface IFormScope extends IScope {
    create : boolean;
    showError;
    addParagraph() : void;
    submit() : angular.IPromise<any>;
}


var postCreate = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    poolPath : string
) => {
    var doc = new RIDocument({preliminaryNames: adhPreliminaryNames});
    doc.parent = poolPath;
    doc.data[SIName.nick] = new SIName.Sheet({
        name: AdhUtil.normalizeName(scope.data.title)
    });

    var paragraphItems = [];
    var paragraphVersions = [];

    _.forEach(scope.data.paragraphs, (paragraph) => {
        var item = new RIParagraph({preliminaryNames: adhPreliminaryNames});
        item.parent = doc.path;

        var version = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
        version.parent = item.path;
        version.data[SIVersionable.nick] = new SIVersionable.Sheet({
            follows: [item.first_version_path]
        });
        version.data[SIParagraph.nick] = new SIParagraph.Sheet({
            text: paragraph.body
        });

        paragraphItems.push(item);
        paragraphVersions.push(version);
    });

    var documentVersion = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
    documentVersion.parent = doc.path;
    documentVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [doc.first_version_path]
    });
    documentVersion.data[SIDocument.nick] = new SIDocument.Sheet({
        title: scope.data.title,
        description: "",
        elements: <string[]>_.map(paragraphVersions, "path")
    });

    return adhHttp.deepPost(<any[]>_.flatten([doc, documentVersion, paragraphItems, paragraphVersions]));
};


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
            scope.data = {
                title: "Toller Titel",
                commentCountTotal: 3
            };
        }
    };
};

export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope) => {
            scope.errors = [];
            scope.data = {
                title: "Toller Titel",
                paragraphs: dummydata
            };
            scope.create = true;
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            scope.submit = () => {
                return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path).then((r) => console.log(r));
            };
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
        link: (scope : IFormScope) => {
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
            AdhImage.moduleName,
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
            "adhConfig", "adhHttp", "adhPermissions", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", createDirective])
        .directive("adhSpdDocumentEdit", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", editDirective])
        .directive("adhSpdDocumentListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", listItemDirective]);
};
