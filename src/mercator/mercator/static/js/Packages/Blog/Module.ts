import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhImageModule = require("../Image/Module");
import AdhListingModule = require("../Listing/Module");
import AdhMarkdownModule = require("../Markdown/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");

import AdhEmbed = require("../Embed/Embed");

import Blog = require("./Blog");


export var moduleName = "adhBlog";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhImageModule.moduleName,
            AdhListingModule.moduleName,
            AdhMarkdownModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
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
            "adhUploadImage",
            Blog.detailDirective])
        .directive("adhBlog", ["adhConfig", Blog.listingDirective])
        .directive("adhBlogPostCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", "adhUploadImage", Blog.createDirective]);
};
