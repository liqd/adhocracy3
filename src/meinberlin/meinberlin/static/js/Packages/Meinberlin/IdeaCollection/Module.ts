import * as AdhAbuseModule from "../../Abuse/Module";
import * as AdhCommentModule from "../../Comment/Module";
import * as AdhHttpModule from "../../Http/Module";
import * as AdhMovingColumnsModule from "../../MovingColumns/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";
import * as AdhPermissionsModule from "../../Permissions/Module";

import * as AdhMeinberlinIdeaCollectionProcessModule from "./Process/Module";
import * as AdhMeinberlinProposalModule from "../Proposal/Module";

import * as IdeaCollection from "./IdeaCollection";


export var moduleName = "adhMeinberlinIdeaCollection";

export var register = (angular) => {
    AdhMeinberlinIdeaCollectionProcessModule.register(angular);

    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMeinberlinIdeaCollectionProcessModule.moduleName,
            AdhMeinberlinProposalModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMeinberlinIdeaCollectionWorkbench", [
            "adhTopLevelState", "adhConfig", "adhHttp", IdeaCollection.workbenchDirective])
        .directive("adhMeinberlinIdeaCollectionProposalDetailColumn", [
            "adhConfig", "adhPermissions", IdeaCollection.proposalDetailColumnDirective])
        .directive("adhMeinberlinIdeaCollectionProposalCreateColumn", [
            "adhConfig", IdeaCollection.proposalCreateColumnDirective])
        .directive("adhMeinberlinIdeaCollectionProposalEditColumn", ["adhConfig", IdeaCollection.proposalEditColumnDirective])
        .directive("adhMeinberlinIdeaCollectionDetailColumn", ["adhConfig", IdeaCollection.detailColumnDirective])
        .directive("adhMeinberlinIdeaCollectionEditColumn", ["adhConfig", IdeaCollection.editColumnDirective])
        .directive("adhMeinberlinIdeaCollectionAddProposalButton", [
            "adhConfig", "adhPermissions", "adhTopLevelState", IdeaCollection.addProposalButtonDirective]);
};
