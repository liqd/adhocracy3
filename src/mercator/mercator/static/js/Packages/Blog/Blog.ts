import AdhConfig = require("../Config/Config");
import AdhDocument = require("../Document/Document");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhMarkdown = require("../Markdown/Markdown");
import AdhPermissions = require("../Permissions/Permissions");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhUtil = require("../Util/Util");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");

var pkgLocation = "/Blog";


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
                unbind = AdhDocument.bindPath($q, adhHttp)(scope);
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

            unbind = AdhDocument.bindPath($q, adhHttp)(scope);
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
            path: "@"
        },
        link: (scope : AdhDocument.IFormScope, element) => {
            scope.errors = [];
            scope.data = {
                title: "",
                paragraphs: [{
                    body: ""
                }]
            };
            scope.showError = adhShowError;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return AdhDocument.postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path);
                }).then((documentVersion : RIDocumentVersion) => {
                    // FIXME: update listing
                });
            };
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
            AdhPermissions.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("blog-post");
            adhEmbedProvider.embeddableDirectives.push("blog-post-create");
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
        .directive("adhBlogPostCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", createDirective]);
};
