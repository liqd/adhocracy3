import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhBadgeModule = require("../Badge/Module");
import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhImageModule = require("../Image/Module");
import AdhInjectModule = require("../Inject/Module");
import AdhMappingModule = require("../Mapping/Module");
import AdhMarkdownModule = require("../Markdown/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhResourceWidgetsModule = require("../ResourceWidgets/Module");
import AdhStickyModule = require("../Sticky/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhDocument = require("./Document");
import AdhEmbed = require("../Embed/Embed");


export var moduleName = "adhDocument";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            "ngMessages",
            AdhAngularHelpersModule.moduleName,
            AdhHttpModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhImageModule.moduleName,
            AdhInjectModule.moduleName,
            AdhMappingModule.moduleName,
            AdhMarkdownModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhResourceWidgetsModule.moduleName,
            AdhStickyModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("document-detail");
            adhEmbedProvider.embeddableDirectives.push("document-create");
            adhEmbedProvider.embeddableDirectives.push("document-edit");
            adhEmbedProvider.embeddableDirectives.push("document-list-item");
        }])
        .directive("adhDocumentDetail", ["$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", AdhDocument.detailDirective])
        .directive("adhDocumentCreate", [
            "$location",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            "adhUploadImage",
            "flowFactory",
            AdhDocument.createDirective])
        .directive("adhDocumentEdit", [
            "$location",
            "$q",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            "adhUploadImage",
            "flowFactory",
            AdhDocument.editDirective])
        .directive("adhDocumentListing", ["adhConfig", AdhDocument.listingDirective])
        .directive("adhDocumentListItem", [
            "$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", AdhDocument.listItemDirective])
        .directive("adhDocumentMapListItem", [
            "$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", AdhDocument.mapListItemDirective]);
};
