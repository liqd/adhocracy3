/// <reference path="../../../../../lib2/types/angular.d.ts"/>

import * as AdhBadge from "../../Badge/Badge";
import * as AdhConfig from "../../Config/Config";
import * as AdhHttp from "../../Http/Http";
import * as AdhPermissions from "../../Permissions/Permissions";
import * as AdhProcess from "../../Process/Process";
import * as AdhProposal from "../../Proposal/Proposal";
import * as AdhRate from "../../Rate/Rate";
import * as AdhTopLevelState from "../../TopLevelState/TopLevelState";


export var pkgLocation = "/Core/IdeaCollection/Poll";


export var pollDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/PollDetailColumn.html",
        scope: {
            processProperties: "=",
            transclusionId: "=",
            view: "=?"
        },
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("contentType", scope));
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
        }
    };
};

export var detailDirective = (
    processType? : string
) => (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhProcess : AdhProcess.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadgeAssignments,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@",
            processProperties: "=?",
        },
        link: (scope) => {
            if (!scope.processProperties && processType) {
                scope.processProperties = adhProcess.getProperties(processType);
            }
            AdhProposal.bindPath(adhConfig, adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(scope);

            scope.goToLogin = () => {
                adhTopLevelState.setCameFromAndGo("/login");
            };
        }
    };
};
