import * as AdhAbuseModule from "../../Abuse/Module";
import * as AdhCommentModule from "../../Comment/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhMovingColumnsModule from "../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";
import * as AdhIdeaCollectionModule from "../../IdeaCollection/Module";
import * as AdhProcessModule from "../../Process/Module";
import * as AdhResourceActionsModule from "../../ResourceActions/Module";
import * as AdhResourceAreaModule from "../../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as AdhProposalModule from "../Proposal/Module";

import * as AdhIdeaCollectionWorkbench from "../../IdeaCollection/Workbench/Workbench";
import * as AdhProcess from "../../Process/Process";
import * as AdhResourceArea from "../../ResourceArea/ResourceArea";

import RIPcompassProcess from "../../../Resources_/adhocracy_pcompass/resources/request/IProcess";
import RIProposal from "../../../Resources_/adhocracy_core/resources/proposal/IProposal";
import RIProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";

import * as Workbench from "./Workbench";


export var moduleName = "adhPcompassWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhIdeaCollectionModule.moduleName,
            AdhProcessModule.moduleName,
            AdhProposalModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollectionWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            var registerRoutes = AdhIdeaCollectionWorkbench.registerRoutesFactory(
                    RIPcompassProcess, RIProposal, RIProposalVersion);
            registerRoutes()(adhResourceAreaProvider);
            adhResourceAreaProvider.processHeaderSlots[RIPcompassProcess.content_type] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[RIPcompassProcess.content_type] =
                    "<adh-idea-collection-workbench data-process-options=\"processOptions\">" +
                    "</adh-idea-collection-workbench>";
            adhProcessProvider.processOptions[RIPcompassProcess.content_type] = {
                hasImage: true,
                proposalClass: RIProposal,
                proposalVersionClass: RIProposalVersion
            };
        }])
        .directive("adhPcompassWorkbench", ["adhTopLevelState", "adhConfig", "adhHttp", Workbench.workbenchDirective])
        .directive("adhPcompassProposalDetailColumn", [
            "$timeout", "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.proposalDetailColumnDirective])
        .directive("adhPcompassProposalCreateColumn", ["adhConfig", "adhTopLevelState", Workbench.proposalCreateColumnDirective])
        .directive("adhPcompassProposalEditColumn", ["adhConfig", "adhTopLevelState", Workbench.proposalEditColumnDirective])
        .directive("adhPcompassProcessDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.processDetailColumnDirective]);
};
