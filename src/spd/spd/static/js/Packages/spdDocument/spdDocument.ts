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

import AdhCommentAdapter = require("../Comment/Adapter");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/spdDocument";


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

    documentVersion? : RIDocumentVersion;
    paragraphVersions? : RIParagraphVersion[];
}

export interface IFormScope extends IScope {
    showError;
    addParagraph() : void;
    submit() : angular.IPromise<any>;
    cancel() : void;
    spdDocumentForm : any;
}


var bindPath = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service<any>
) => (
    scope : IScope,
    pathKey : string = "path"
) => {
    var commentableAdapter = new AdhCommentAdapter.ListingCommentableAdapter();

    scope.$watch(pathKey, (path : string) => {
        if (path) {
            adhHttp.get(path).then((documentVersion : RIDocumentVersion) => {
                var paragraphPaths : string[] = documentVersion.data[SIDocument.nick].elements;
                var paragraphPromises = _.map(paragraphPaths, (path) => adhHttp.get(path));

                return $q.all(paragraphPromises).then((paragraphVersions : RIParagraphVersion[]) => {
                    var paragraphs = _.map(paragraphVersions, (paragraphVersion) => {
                        return {
                            body: paragraphVersion.data[SIParagraph.nick].text,
                            commentCount: commentableAdapter.totalCount(paragraphVersion),
                            path: paragraphVersion.path
                        };
                    });

                    scope.documentVersion = documentVersion;
                    scope.paragraphVersions = paragraphVersions;

                    scope.data = {
                        title: documentVersion.data[SIDocument.nick].title,
                        paragraphs: paragraphs,
                        // FIXME: DefinitelyTyped
                        commentCountTotal: (<any>_).sum(_.map(paragraphs, "commentCount"))
                    };
                });
            });
        }
    });
};

var postCreate = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    poolPath : string
) : angular.IPromise<RIDocumentVersion> => {
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

    return adhHttp.deepPost(<any[]>_.flatten([doc, documentVersion, paragraphItems, paragraphVersions]))
        .then((result) => result[1]);
};

var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    oldVersion : RIDocumentVersion,
    oldParagraphVersions : RIParagraphVersion[]
) : angular.IPromise<RIDocumentVersion> => {
    // This function assumes that paragraphs can not be reordered or deleted
    // and that new paragraphs are always appended to the end.

    var documentPath = AdhUtil.parentPath(oldVersion.path);

    var paragraphItems : RIParagraph[] = [];
    var paragraphVersions : RIParagraphVersion[] = [];
    var paragraphRefs : string[] = [];

    var paragraphVersion : RIParagraphVersion;

    _.forEach(scope.data.paragraphs, (paragraph : IParagraph, index : number) => {
        if (index >= oldParagraphVersions.length) {
            var item = new RIParagraph({preliminaryNames: adhPreliminaryNames});
            item.parent = documentPath;

            paragraphVersion = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
            paragraphVersion.parent = item.path;
            paragraphVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
                follows: [item.first_version_path]
            });
            paragraphVersion.data[SIParagraph.nick] = new SIParagraph.Sheet({
                text: paragraph.body
            });
            paragraphVersion.root_versions = [oldVersion.path];

            paragraphItems.push(item);
            paragraphVersions.push(paragraphVersion);
            paragraphRefs.push(paragraphVersion.path);
        } else {
            var oldParagraphVersion = oldParagraphVersions[index];

            if (paragraph.body !== oldParagraphVersion.data[SIParagraph.nick].text) {
                paragraphVersion = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
                paragraphVersion.parent = AdhUtil.parentPath(oldParagraphVersion.path);
                paragraphVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
                    follows: [oldParagraphVersion.path]
                });
                paragraphVersion.data[SIParagraph.nick] = new SIParagraph.Sheet({
                    text: paragraph.body
                });
                paragraphVersion.root_versions = [oldVersion.path];

                paragraphVersions.push(paragraphVersion);
                paragraphRefs.push(paragraphVersion.path);
            } else {
                paragraphRefs.push(oldParagraphVersion.path);
            }
        }
    });

    var documentVersion = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
    documentVersion.parent = documentPath;
    documentVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [oldVersion.path]
    });
    documentVersion.data[SIDocument.nick] = new SIDocument.Sheet({
        title: scope.data.title,
        description: "",
        elements: paragraphRefs
    });

    return adhHttp.deepPost(<any[]>_.flatten([documentVersion, paragraphItems, paragraphVersions]))
        .then((result) => result[0]);
};


export var detailDirective = (
    $q : angular.IQService,
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
            bindPath($q, adhHttp)(scope);
        }
    };
};

export var listItemDirective = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath($q, adhHttp)(scope);

            scope.$on("$destroy", adhTopLevelState.on("documentUrl", (documentVersionUrl) => {
                if (!documentVersionUrl) {
                    scope.selectedState = "";
                } else if (documentVersionUrl === scope.path) {
                    scope.selectedState = "is-selected";
                } else {
                    scope.selectedState = "is-not-selected";
                }
            }));
        }
    };
};

export var listingDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.contentType = RIDocumentVersion.content_type;
        }
    };
};

export var createDirective = (
    $location : angular.ILocationService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid,
    adhResourceUrlFilter
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.data = {
                title: "",
                paragraphs: [{
                    body: ""
                }]
            };
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            scope.cancel = () => {
                var processUrl = adhTopLevelState.get("processUrl");
                adhTopLevelState.redirectToCameFrom(adhResourceUrlFilter(processUrl));
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.spdDocumentForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path);
                }).then((documentVersion : RIDocumentVersion) => {
                    var itemPath = AdhUtil.parentPath(documentVersion.path);
                    $location.url(adhResourceUrlFilter(itemPath));
                }, (errors) => {
                    scope.errors = errors;
                });
            };
        }
    };
};

export var editDirective = (
    $location : angular.ILocationService,
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid,
    adhResourceUrlFilter
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            bindPath($q, adhHttp)(scope);

            scope.cancel = () => {
                adhTopLevelState.redirectToCameFrom(adhResourceUrlFilter(scope.documentVersion.path));
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.spdDocumentForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.documentVersion, scope.paragraphVersions);
                }).then((documentVersion : RIDocumentVersion) => {
                    var itemPath = AdhUtil.parentPath(documentVersion.path);
                    $location.url(adhResourceUrlFilter(itemPath));
                }, (errors) => {
                    scope.errors = errors;
                });
            };
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
            "$q", "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", detailDirective])
        .directive("adhSpdDocumentCreate", [
            "$location",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            createDirective])
        .directive("adhSpdDocumentEdit", [
            "$location",
            "$q",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            editDirective])
        .directive("adhSpdListing", ["adhConfig", listingDirective])
        .directive("adhSpdDocumentListItem", [
            "$q", "adhConfig", "adhHttp", "adhTopLevelState", listItemDirective]);
};
