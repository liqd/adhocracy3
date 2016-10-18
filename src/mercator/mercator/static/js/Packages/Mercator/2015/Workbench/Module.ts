import * as AdhAbuseModule from "../../../Core/Abuse/Module";
import * as AdhCommentModule from "../../../Core/Comment/Module";
import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhListingModule from "../../../Core/Listing/Module";
import * as AdhMovingColumnsModule from "../../../Core/MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Core/Permissions/Module";
import * as AdhResourceActionsModule from "../../../Core/ResourceActions/Module";
import * as AdhResourceAreaModule from "../../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../../Core/TopLevelState/Module";
import * as AdhUserModule from "../../../Core/User/Module";

import RIProcess from "../../../../Resources_/adhocracy_mercator/resources/mercator/IProcess";

import * as AdhMercator2015ProposalModule from "../Proposal/Module";

import * as Workbench from "./Workbench";


export var moduleName = "adhMercator2015Workbench";

export var register = (angular) => {
    var processType = RIProcess.content_type;

    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhListingModule.moduleName,
            AdhMercator2015ProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhUserModule.moduleName
        ])
        .config(["adhResourceAreaProvider", Workbench.registerRoutes(RIProcess.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider) => {
            adhProcessProvider.templates[processType] =
                "<adh-mercator-2015-workbench></adh-mercator-2015-workbench>";
        }])
        .directive("adhMercator2015Workbench", ["adhConfig", "adhTopLevelState", Workbench.workbenchDirective])
        .directive("adhMercator2015ProposalCreateColumn", [
            "adhConfig", "adhTopLevelState", "adhResourceUrlFilter", "$location", Workbench.proposalCreateColumnDirective])
        .directive("adhMercator2015ProposalDetailColumn", [
            "adhTopLevelState", "adhPermissions", "adhConfig", Workbench.proposalDetailColumnDirective])
        .directive("adhMercator2015ProposalEditColumn", [
            "adhConfig", "adhTopLevelState", "adhResourceUrlFilter", "$location", Workbench.proposalEditColumnDirective])
        .directive("adhMercator2015ProposalListingColumn",
            ["adhConfig", "adhHttp", "adhTopLevelState", Workbench.proposalListingColumnDirective]);
};
