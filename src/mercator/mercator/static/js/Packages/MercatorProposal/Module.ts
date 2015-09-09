import * as AdhAngularHelpersModule from "../AngularHelpers/Module";
import * as AdhBadgeModule from "../Badge/Module";
import * as AdhCredentialsModule from "../User/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhImageModule from "../Image/Module";
import * as AdhInjectModule from "../Inject/Module";
import * as AdhLocaleModule from "../Locale/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../PreliminaryNames/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhResourceWidgetsModule from "../ResourceWidgets/Module";
import * as AdhStickyModule from "../Sticky/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhUtil from "../Util/Util";

import RIProcess from "../../Resources_/adhocracy_mercator/resources/mercator/IProcess";

import * as MercatorProposal from "./MercatorProposal";


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
