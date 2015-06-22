import AdhConfig = require("../Config/Config");
import AdhDocument = require("../Document/Document");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");

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


export var moduleName = "adhBlog";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhHttp.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("blog-post");
        }])
        .directive("adhBlogPost", ["$q", "adhConfig", "adhHttp", detailDirective]);
};
