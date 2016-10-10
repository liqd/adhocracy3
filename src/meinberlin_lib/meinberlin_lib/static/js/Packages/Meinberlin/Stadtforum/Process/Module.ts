import * as AdhConfigModule from "../../../Core/Config/Module";
import * as AdhEmbedModule from "../../../Core/Embed/Module";
import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhNamesModule from "../../../Core/Names/Module";
import * as AdhPermissionsModule from "../../../Core/Permissions/Module";
import * as AdhProcessModule from "../../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../../Core/ResourceArea/Module";

import * as AdhNames from "../../../Core/Names/Names";
import * as AdhProcess from "../../../Core/Process/Process";

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
            AdhNamesModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] = "<adh-meinberlin-stadtforum-workbench></adh-meinberlin-stadtforum-workbench>";
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[processType] = "TR__RESOURCE_STADTFORUM";
            adhNamesProvider.names[RIProposalVersion.content_type] = "TR__RESOURCE_POLL";
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider, adhConfig) => {
            Process.registerRoutes(processType)(adhResourceAreaProvider);
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
