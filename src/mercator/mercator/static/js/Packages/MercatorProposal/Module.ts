import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhBadgeModule = require("../Badge/Module");
import AdhCredentialsModule = require("../User/Module");
import AdhHttpModule = require("../Http/Module");
import AdhImageModule = require("../Image/Module");
import AdhInjectModule = require("../Inject/Module");
import AdhLocaleModule = require("../Locale/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhResourceWidgetsModule = require("../ResourceWidgets/Module");
import AdhStickyModule = require("../Sticky/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhUtil = require("../Util/Util");

import RIProcess = require("../../Resources_/adhocracy_mercator/resources/mercator/IProcess");

import MercatorProposal = require("./MercatorProposal");


export var moduleName = "adhMercatorProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            "ngMessages",
            AdhAngularHelpersModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhCredentialsModule.moduleName,
            AdhHttpModule.moduleName,
            AdhImageModule.moduleName,
            AdhInjectModule.moduleName,
            AdhLocaleModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhResourceWidgetsModule.moduleName,
            AdhStickyModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", MercatorProposal.registerRoutes(RIProcess.content_type)])
        .config(["flowFactoryProvider", (flowFactoryProvider) => {
            if (typeof flowFactoryProvider.defaults === "undefined") {
                flowFactoryProvider.defaults = {};
            }
            flowFactoryProvider.defaults = {
                singleFile: true,
                maxChunkRetries: 1,
                chunkRetryInterval: 5000,
                simultaneousUploads: 4,
                permanentErrors: [404, 500, 501, 502, 503],
                // these are not native to flow but used by custom functions
                minimumWidth: 400,
                maximumByteSize: 3000000,
                acceptedFileTypes: [
                    "gif",
                    "jpeg",
                    "png"
                ]  // correspond to exact mime types EG image/png
            };
        }])
        // NOTE: we do not use a Widget based directive here for performance reasons
        .directive("adhMercatorProposal", ["$q", "adhConfig", "adhHttp", "adhTopLevelState", "adhGetBadges", MercatorProposal.listItem])
        .directive("adhMercatorProposalDetailView", [
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhGetBadges",
            "adhUploadImage",
            "flowFactory",
            "moment",
            "$window",
            "$location",
            "$q",
            (...args) => {
                var widget = AdhUtil.construct(MercatorProposal.DetailWidget, args);
                return widget.createDirective();
            }])
        .directive("adhMercatorProposalCreate", [
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhGetBadges",
            "adhUploadImage",
            "$timeout",
            "flowFactory",
            "moment",
            "modernizr",
            "$window",
            "$location",
            "$q",
            (...args) => {
                var widget = AdhUtil.construct(MercatorProposal.CreateWidget, args);
                return widget.createDirective();
            }])
        .directive("adhMercatorProposalListing", ["adhConfig", MercatorProposal.listing])
        .directive("adhMercatorUserProposalListing", ["adhConfig", MercatorProposal.userListing])
        .directive("adhMercatorProposalAddButton", [
            "adhConfig",
            "adhHttp",
            "adhTopLevelState",
            "adhPermissions",
            "adhCredentials",
            "$q",
            MercatorProposal.addButton
            ])
        .controller("mercatorProposalFormController", [
            "$scope", "$element", "$window", "adhShowError", "adhSubmitIfValid", MercatorProposal.mercatorProposalFormController]);
};
