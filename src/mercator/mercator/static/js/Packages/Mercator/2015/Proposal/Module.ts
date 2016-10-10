import * as AdhAngularHelpersModule from "../../../Core/AngularHelpers/Module";
import * as AdhBadgeModule from "../../../Core/Badge/Module";
import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhImageModule from "../../../Core/Image/Module";
import * as AdhInjectModule from "../../../Core/Inject/Module";
import * as AdhLocaleModule from "../../../Core/Locale/Module";
import * as AdhMetaApiModule from "../../../Core/MetaApi/Module";
import * as AdhNamesModule from "../../../Core/Names/Module";
import * as AdhPermissionsModule from "../../../Core/Permissions/Module";
import * as AdhPreliminaryNamesModule from "../../../Core/PreliminaryNames/Module";
import * as AdhResourceAreaModule from "../../../Core/ResourceArea/Module";
import * as AdhResourceWidgetsModule from "../../../ResourceWidgets/Module";
import * as AdhStickyModule from "../../../Core/Sticky/Module";
import * as AdhTopLevelStateModule from "../../../Core/TopLevelState/Module";

import * as AdhBlogModule from "../../../Blog/Module";

import * as AdhNames from "../../../Core/Names/Names";
import * as AdhUtil from "../../../Core/Util/Util";

import RIMercator2015Process from "../../../../Resources_/adhocracy_mercator/resources/mercator/IProcess";
import RIProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";

import * as Proposal from "./Proposal";


export var moduleName = "adhMercator2015Proposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            "ngMessages",
            AdhAngularHelpersModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhBlogModule.moduleName,
            AdhHttpModule.moduleName,
            AdhImageModule.moduleName,
            AdhInjectModule.moduleName,
            AdhLocaleModule.moduleName,
            AdhMetaApiModule.moduleName,
            AdhNamesModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhResourceWidgetsModule.moduleName,
            AdhStickyModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhConfig", "adhMetaApiProvider", (
            adhResourceAreaProvider,
            adhConfig,
            adhMetaApi
        ) => {
            var processType = RIMercator2015Process.content_type;
            var processHeaderSlot = adhConfig.pkg_path + Proposal.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
            Proposal.registerRoutes(processType)(adhResourceAreaProvider, adhMetaApi);
        }])
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
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIProposalVersion.content_type] = "TR__RESOURCE_PROPOSAL";
        }])
        // NOTE: we do not use a Widget based directive here for performance reasons
        .directive("adhMercator2015Proposal", ["adhConfig", "adhHttp", "adhTopLevelState", "adhGetBadges", Proposal.listItem])
        .directive("adhMercator2015ProposalDetailView", [
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
                var widget = AdhUtil.construct(Proposal.DetailWidget, args);
                return widget.createDirective();
            }])
        .directive("adhMercator2015ProposalCreate", [
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
                var widget = AdhUtil.construct(Proposal.CreateWidget, args);
                return widget.createDirective();
            }])
        .directive("adhMercator2015ProposalListing", ["adhConfig", Proposal.listing])
        .directive("adhMercator2015UserProposalListing", ["adhConfig", Proposal.userListing])
        .directive("adhMercator2015AddProposalButton", ["adhConfig", "adhPermissions", "adhTopLevelState", Proposal.addProposalButton])
        .controller("mercatorProposalFormController", [
            "$scope", "$element", "$window", "adhShowError", "adhSubmitIfValid", Proposal.mercatorProposalFormController]);
};
