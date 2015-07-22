import AdhConfig = require("../Config/Config");
import AdhDocument = require("../Document/Document");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhMarkdown = require("../Markdown/Markdown");
import AdhPermissions = require("../Permissions/Permissions");
import AdhListing = require("../Listing/Listing");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhUtil = require("../Util/Util");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");

var pkgLocation = "/Blog";


export interface IScope extends AdhDocument.IScope {
    titles : {
        value : string;
        title : string;
    }[];
}

export interface IFormScope extends IScope, AdhDocument.IFormScope {
    onSubmit() : void;
}

export var bindPath = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service<any>
) => {
    var fn = AdhDocument.bindPath($q, adhHttp);

    return (
        scope : IScope,
        pathKey : string = "path"
    ) : Function => {
        scope.titles = [
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
            }
        ];

        return fn(scope, pathKey);
    };
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

            scope.delete = () => {
                if ($window.confirm("Do you really want to delete this?")) {
                    var itemPath = AdhUtil.parentPath(scope.path);
                    adhHttp.delete(itemPath, RIDocument.content_type)
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
            scope.titles = [
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
                }
            ];
            scope.data = {
                title: "",
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
