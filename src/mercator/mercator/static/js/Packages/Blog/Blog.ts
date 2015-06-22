import AdhConfig = require("../Config/Config");
import AdhDocument = require("../Document/Document");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");

var pkgLocation = "/Blog";


export var detailDirective = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : AdhDocument.IScope) => {
            AdhDocument.bindPath($q, adhHttp)(scope);
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
                }, (errors) => {
                    scope.errors = errors;
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
            AdhHttp.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("blog-post");
            adhEmbedProvider.embeddableDirectives.push("blog-post-create");
        }])
        .directive("adhBlogPost", ["$q", "adhConfig", "adhHttp", detailDirective])
        .directive("adhBlogPostCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", createDirective]);
};
