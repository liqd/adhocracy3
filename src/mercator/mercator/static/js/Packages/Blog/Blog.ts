import AdhConfig = require("../Config/Config");
import AdhDocument = require("../Document/Document");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhMarkdown = require("../Markdown/Markdown");
import AdhPermissions = require("../Permissions/Permissions");
import AdhListing = require("../Listing/Listing");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhUtil = require("../Util/Util");

import AdhCommentAdapter = require("../Comment/Adapter");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");

import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIMetadata = require("../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIImageReference = require("../../Resources_/adhocracy_core/sheets/image/IImageReference");


var pkgLocation = "/Blog";


export interface IFormScope extends AdhDocument.IFormScope {
    onSubmit() : void;
}


export var bindPath = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service<any>
) => (
    scope : any,
    pathKey : string = "path"
) : Function => {
    var commentableAdapter = new AdhCommentAdapter.ListingCommentableAdapter();

    return scope.$watch(pathKey, (path : string) => {
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
                        title: documentVersion.data[SITitle.nick].title,
                        titles: [
                            {
                                value: "challenge",
                                title: "Challenge"
                            },
                            {
                                value: "highlight",
                                title: "Highlight"
                            },
                            {
                                value: "team story",
                                title: "Team Story"
                            },
                            {
                                value: "other title",
                                title: "Other Title"
                            }
                        ],
                        paragraphs: paragraphs,
                        // FIXME: DefinitelyTyped
                        commentCountTotal: (<any>_).sum(_.map(paragraphs, "commentCount")),
                        modificationDate: documentVersion.data[SIMetadata.nick].modification_date,
                        creationDate: documentVersion.data[SIMetadata.nick].creation_date,
                        creator: documentVersion.data[SIMetadata.nick].creator,
                        picture: documentVersion.data[SIImageReference.nick].picture
                    };
                });
            });
        }
    });
};



export var detailDirective = (
    $q : angular.IQService,
    $window : angular.IWindowService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope, element) => {
            var unbind : Function;

            scope.errors = [];
            scope.showError = adhShowError;
            scope.mode = "display";

            adhPermissions.bindScope(scope, () => scope.path);
            adhPermissions.bindScope(scope, () => AdhUtil.parentPath(scope.path), "itemOptions");

            scope.hide = () => {
                if ($window.confirm("Do you really want to delete this?")) {
                    var itemPath = AdhUtil.parentPath(scope.path);
                    adhHttp.hide(itemPath, RIDocument.content_type)
                        .then(() => {
                            if (typeof scope.onChange !== "undefined") {
                                scope.onChange();
                            }
                        });
                }
            };

            scope.edit = () => {
                scope.mode = "edit";
                unbind();
            };

            scope.cancel = () => {
                scope.mode = "display";
                unbind = bindPath($q, adhHttp)(scope);
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return AdhDocument.postEdit(adhHttp, adhPreliminaryNames)(scope, scope.documentVersion, scope.paragraphVersions);
                }).then((documentVersion : RIDocumentVersion) => {
                    if (typeof scope.onChange !== "undefined") {
                        scope.onChange();
                    }
                });
            };

            unbind = bindPath($q, adhHttp)(scope);
        }
    };
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
            onSubmit: "=?"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.data = {
                title: "",
                titles: [
                    {
                        value: "challenge",
                        title: "Challenge"
                    },
                    {
                        value: "highlight",
                        title: "Highlight"
                    },
                    {
                        value: "team story",
                        title: "Team Story"
                    },
                    {
                        value: "other title",
                        title: "Other Title"
                    }
                ],
                paragraphs: [{
                    body: ""
                }]
            };
            scope.showError = adhShowError;
            scope.showCreateForm = false;

            scope.toggleCreateForm = () => {
                scope.showCreateForm = true;
            };

            scope.cancel = () => {
                scope.data.paragraphs[0].body = "";
                scope.data.title = "";
                scope.documentForm.$setPristine();
                scope.showCreateForm = false;
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return AdhDocument.postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path);
                }).then((documentVersion : RIDocumentVersion) => {

                    scope.cancel();

                    if (typeof scope.onSubmit !== "undefined") {
                        scope.onSubmit();
                    }
                }, (errors) => {
                    scope.errors = errors;
                });
            };
        }
    };
};

export var listingDirective = (adhConfig : AdhConfig.IService) => {
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


export var moduleName = "adhBlog";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhHttp.moduleName,
            AdhMarkdown.moduleName,
            AdhPermissions.moduleName,
            AdhListing.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("blog-post");
            adhEmbedProvider.embeddableDirectives.push("blog-post-create");
            adhEmbedProvider.embeddableDirectives.push("blog");
        }])
        .directive("adhBlogPost", [
            "$q",
            "$window",
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhPreliminaryNames",
            "adhShowError",
            "adhSubmitIfValid",
            detailDirective])
        .directive("adhBlog", ["adhConfig", listingDirective])
        .directive("adhBlogPostCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", createDirective]);
};
