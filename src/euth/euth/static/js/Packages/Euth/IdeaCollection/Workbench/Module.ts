import * as AdhAbuseModule from "../../../Abuse/Module";
import * as AdhCommentModule from "../../../Comment/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhIdeaCollectionModule from "../../../IdeaCollection/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhProcessModule from "../../../Process/Module";
import * as AdhProposalModule from "../Proposal/Module";
import * as AdhResourceActionsModule from "../../../ResourceActions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhIdeaCollectionWorkbench from "../../../IdeaCollection/Workbench/Workbench";
import * as AdhProcess from "../../../Process/Process";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import RIEuthProcess from "../../../../Resources_/adhocracy_euth/resources/idea_collection/IProcess";
import RIEuthPrivateProcess from "../../../../Resources_/adhocracy_euth/resources/idea_collection/IPrivateProcess";
import RIProposal from "../../../../Resources_/adhocracy_core/resources/proposal/IProposal";
import RIProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";

import * as Workbench from "./Workbench";


export var moduleName = "adhEuthWorkbench";

var processType1 = RIEuthProcess.content_type;
var processType2 = RIEuthPrivateProcess.content_type;

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhIdeaCollectionModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhProposalModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var registerRoutes1 = AdhIdeaCollectionWorkbench.registerRoutesFactory(
                RIEuthProcess, RIProposal, RIProposalVersion);
            registerRoutes1()(adhResourceAreaProvider);
            var registerRoutes2 = AdhIdeaCollectionWorkbench.registerRoutesFactory(
                RIEuthPrivateProcess, RIProposal, RIProposalVersion);
            registerRoutes2()(adhResourceAreaProvider);
            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollectionWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType1] = processHeaderSlot;
            adhResourceAreaProvider.processHeaderSlots[processType2] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType1] =
                "<adh-idea-collection-workbench data-process-options=\"processOptions\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.processOptions[processType1] = {
                hasImage: true,
                proposalClass: RIProposal,
                proposalVersionClass: RIProposalVersion
            };
            adhProcessProvider.templates[processType2] =
                "<adh-idea-collection-workbench data-process-options=\"processOptions\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.processOptions[processType2] = {
                hasImage: true,
                proposalClass: RIProposal,
                proposalVersionClass: RIProposalVersion
            };
        }])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(RIEuthProcess)])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(RIEuthPrivateProcess)])
        .directive("adhPcompassWorkbench", ["adhTopLevelState", "adhConfig", "adhHttp", Workbench.workbenchDirective])
        .directive("adhPcompassProposalDetailColumn", [
            "$timeout", "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.proposalDetailColumnDirective])
        .directive("adhPcompassProposalCreateColumn", ["adhConfig", "adhTopLevelState", Workbench.proposalCreateColumnDirective])
        .directive("adhPcompassProposalEditColumn", ["adhConfig", "adhTopLevelState", Workbench.proposalEditColumnDirective])
        .directive("adhPcompassProposalImageColumn", [
            "adhConfig", "adhTopLevelState", "adhResourceUrlFilter", "adhParentPathFilter", Workbench.proposalImageColumnDirective])
        .directive("adhPcompassProcessDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.processDetailColumnDirective]);
};
