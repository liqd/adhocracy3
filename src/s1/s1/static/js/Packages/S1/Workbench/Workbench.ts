/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../../Config/Config");
import AdhHttp = require("../../Http/Http");
import AdhMovingColumns = require("../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../Permissions/Permissions");
import AdhProcess = require("../../Process/Process");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../TopLevelState/TopLevelState");
import AdhUtil = require("../../Util/Util");

import RIS1Process = require("../../../Resources_/adhocracy_s1/resources/s1/IProcess");
import RIProposal = require("../../../Resources_/adhocracy_s1/resources/s1/IProposal");
import RIProposalVersion = require("../../../Resources_/adhocracy_s1/resources/s1/IProposalVersion");
import SIWorkflowAssignment = require("../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment");

var pkgLocation = "/S1/Workbench";


export var s1WorkbenchDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
        }
    };
};


export var s1ProposalDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
            adhPermissions.bindScope(scope, () => scope.proposalUrl && AdhUtil.parentPath(scope.proposalUrl), "proposalItemOptions");
        }
    };
};

export var s1ProposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
        }
    };
};

export var s1ProposalEditColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
        }
    };
};


/**
 *         | proposed | votable | selected | rejected
 * --------------------------------------------------
 * propose | current  | -       | archive  | archive
 * select  | next     | current | archive  | archive
 * result  | next     | -       | cur/arc  | cur/arc
 *
 * FIXME: currently it is not possible to distinguish whether
 * selected/rejected proposals in the result state are results of the
 * current iteration or archived. The current implementation treats
 * them as archived.
 */
var getMeeting = (proposal : RIProposal, process : RIS1Process) => {
    var processState = process.data[SIWorkflowAssignment.nick].workflow_state;
    var proposalState = proposal.data[SIWorkflowAssignment.nick].workflow_state;

    if (proposalState === "proposed") {
        return processState === "propose" ? "current" : "next";
    } else if (proposalState === "votable") {
        return "current";
    } else {
        return "archive";
    }
};


export var registerRoutes = (
    processType : string = "",
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider
        .default(RIS1Process, "", processType, context, {
            space: "content",
            meeting: "current",
            movingColumns: "is-show-hide-hide"
        })
        .default(RIS1Process, "create-proposal", processType, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .specific(RIS1Process, "create-proposal", processType, context,
            ["adhHttp", (adhHttp : AdhHttp.Service<any>) => {
                return (resource : RIS1Process) => {
                    return adhHttp.options(resource.path).then((options) => {
                        if (options.POST) {
                            var processState = resource.data[SIWorkflowAssignment.nick].workflow_stat;
                            return {
                                meeting: processState === "propose" ? "current" : "next"
                            };
                        } else {
                            throw 401;
                        }
                    });
                };
            }])
        .default(RIS1Process, "archive", processType, context, {
            space: "content",
            meeting: "archive",
            movingColumns: "is-show-hide-hide"
        })
        .default(RIS1Process, "next", processType, context, {
            space: "content",
            meeting: "next",
            movingColumns: "is-show-hide-hide"
        })

        .defaultVersionable(RIProposal, RIProposalVersion, "", processType, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIProposal, RIProposalVersion, "", processType, context, () => {
            return (item : RIProposal, version : RIProposalVersion, isVersion : boolean, process : RIS1Process) => {
                return {
                    proposalUrl: version.path,
                    meeting: getMeeting(item, process)
                };
            };
        })
        .defaultVersionable(RIProposal, RIProposalVersion, "edit", processType, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIProposal, RIProposalVersion, "edit", processType, context,
            ["adhHttp", (adhHttp : AdhHttp.Service<any>) => {
                return (item : RIProposal, version : RIProposalVersion, isVersion : boolean, process : RIS1Process) => {
                    return adhHttp.options(item.path).then((options) => {
                        if (options.POST) {
                            return {
                                proposalUrl: version.path,
                                meeting: getMeeting(item, process)
                            };
                        } else {
                            throw 401;
                        }
                    });
                };
            }])
        .defaultVersionable(RIProposal, RIProposalVersion, "comments", processType, context, {
            space: "content",
            movingColumns: "is-collapse-show-show"
        })
        .specificVersionable(RIProposal, RIProposalVersion, "comments", processType, context, () => {
            return (item : RIProposal, version : RIProposalVersion, isVersion : boolean, process : RIS1Process) => {
                return {
                    proposalUrl: version.path,
                    meeting: getMeeting(item, process)
                };
            };
        });
};


export var moduleName = "adhS1Workbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhResourceAreaProvider", registerRoutes(RIS1Process.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIS1Process.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-s1-workbench></adh-s1-workbench>");
            }];
        }])
        .directive("adhS1Workbench", ["adhConfig", "adhTopLevelState", s1WorkbenchDirective])
        .directive("adhS1ProposalDetailColumn", ["adhConfig", "adhPermissions", s1ProposalDetailColumnDirective])
        .directive("adhS1ProposalCreateColumn", ["adhConfig", s1ProposalCreateColumnDirective])
        .directive("adhS1ProposalEditColumn", ["adhConfig", s1ProposalEditColumnDirective]);
};
