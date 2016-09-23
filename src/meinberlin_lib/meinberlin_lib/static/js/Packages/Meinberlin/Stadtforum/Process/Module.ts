import * as AdhConfigModule from "../../../Config/Module";
import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhHttpModule from "../../../Http/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhProcess from "../../../Process/Process";

import * as Process from "./Process";

import RIProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";
import RIStadtforumProcess from "../../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IProcess";


export var moduleName = "adhMeinberlinStadtforumProcess";

export var register = (angular) => {
    var processType = RIStadtforumProcess.content_type;

    angular
        .module(moduleName, [
            AdhConfigModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.names[processType] = "TR__PROCESS_STADTFORUM";
            adhProcessProvider.templates[processType] = "<adh-meinberlin-stadtforum-workbench></adh-meinberlin-stadtforum-workbench>";
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider, adhConfig) => {
            Process.registerRoutes(processType)(adhResourceAreaProvider);
            adhResourceAreaProvider.names[RIProposalVersion.content_type] = "TR__POLLS";
        }])
        .directive("adhMeinberlinStadtforumWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", Process.workbenchDirective])
        .directive("adhMeinberlinStadtforumProposalDetailColumn", [
            "adhConfig", "adhTopLevelState", Process.proposalDetailColumnDirective])
        .directive("adhMeinberlinStadtforumProposalCreateColumn", [
            "adhConfig", "adhTopLevelState", Process.proposalCreateColumnDirective])
        .directive("adhMeinberlinStadtforumProposalEditColumn", [
            "adhConfig", "adhTopLevelState", Process.proposalEditColumnDirective])
        .directive("adhMeinberlinStadtforumDetailColumn", ["adhConfig", "adhTopLevelState", Process.detailColumnDirective])
        .directive("adhMeinberlinStadtforumDetail", ["adhConfig", "adhEmbed", "adhHttp", "adhPermissions", "$q", Process.detailDirective]);
};
