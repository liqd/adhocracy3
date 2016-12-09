import * as AdhHttpModule from "../Core/Http/Module";
import * as AdhImageModule from "../Core/Image/Module";
import * as AdhListingModule from "../Core/Listing/Module";
import * as AdhMarkdownModule from "../Core/Markdown/Module";
import * as AdhNamesModule from "../Core/Names/Module";
import * as AdhPermissionsModule from "../Core/Permissions/Module";
import * as AdhPreliminaryNamesModule from "../Core/PreliminaryNames/Module";

import * as AdhNames from "../Core/Names/Names";

import * as Blog from "./Blog";

import RIDocumentVersion from "../../Resources_/adhocracy_core/resources/document/IDocumentVersion";


export var moduleName = "adhBlog";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhImageModule.moduleName,
            AdhListingModule.moduleName,
            AdhMarkdownModule.moduleName,
            AdhNamesModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
        ])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIDocumentVersion.content_type] = "TR__RESOURCE_DOCUMENT";
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
            "$translate",
            Blog.detailDirective])
        .directive("adhBlog", ["adhConfig", Blog.listingDirective])
        .directive("adhBlogPostCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", "adhUploadImage", Blog.createDirective]);
};
