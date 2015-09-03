/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhComment = require("../../Comment/Comment");
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
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
            scope.$on("$destroy", adhTopLevelState.bind("meeting", scope));
            scope.$on("$destroy", adhTopLevelState.bind("landingPage", scope));
        }
    };
};


export var s1CurrentColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CurrentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.contentType = RIProposalVersion.content_type;

            scope.$watch("processUrl", (processUrl : string) => {
                adhHttp.get(processUrl).then((process : RIS1Process) => {
                    var workflowState = process.data[SIWorkflowAssignment.nick].workflow_state;
                    var decisionDate = AdhUtil.deepPluck(
                        AdhProcess.getStateData(process.data[SIWorkflowAssignment.nick], "result"), ["start_date"]);

                    if (workflowState === "propose") {
                        scope.proposalState = "proposed";
                    } else if (workflowState === "select") {
                        scope.proposalState = "voteable";
                    } else {
                        scope.proposalState = "[\"any\", [\"selected\", \"rejected\"]]";
                        scope.decisionDate = decisionDate;
                    }
                });
            });

            scope.shared.sort = "rates";
            scope.shared.reverse = true;
            scope.shared.setSort = (sort : string) => {
                scope.shared.sort = sort;
            };
        }
    };
};


export var s1NextColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/NextColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.contentType = RIProposalVersion.content_type;

            scope.$watch("processUrl", (processUrl : string) => {
                adhHttp.get(processUrl).then((process : RIS1Process) => {
                    scope.processState = process.data[SIWorkflowAssignment.nick].workflow_state;

                    if (scope.processState === "propose") {
                        scope.proposalState = "none";
                    } else {
                        scope.proposalState = "proposed";
                    }
                });
            });

            scope.shared.sort = "rates";
            scope.shared.reverse = true;
            scope.shared.setSort = (sort : string) => {
                scope.shared.sort = sort;
            };
        }
    };
};


export var s1ArchiveColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ArchiveColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.contentType = RIProposalVersion.content_type;

            scope.$watch("processUrl", (processUrl : string) => {
                adhHttp.get(processUrl).then((process : RIS1Process) => {
                    scope.proposalState = "[\"any\", [\"selected\", \"rejected\"]]";

                    var workflowState = process.data[SIWorkflowAssignment.nick].workflow_state;
                    if (workflowState === "result") {
                        var decisionDate = AdhUtil.deepPluck(
                            AdhProcess.getStateData(process.data[SIWorkflowAssignment.nick], "result"), ["start_date"]);
                        scope.decisionDate = "[\"lt\",  \"" + decisionDate + "\"]";
                    }
                });
            });

            scope.shared.facets = [{
                key: "sort",
                name: "TR__SORT",
                items: [
                    {key: "rates", name: "TR__RATES"},
                    {key: "title", name: "TR__TITLE"},
                    {key: "item_creation_date", name: "TR__DATE"}
                ]
            }];

            scope.shared.sort = "rates";
            scope.shared.reverse = true;
            scope.shared.setSort = (sort : string) => {
                scope.shared.sort = sort;
            };
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
            column.bindVariablesAndClear(scope, ["meeting", "processUrl", "proposalUrl"]);
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

export var s1LandingDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Landing.html"
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
        var processDecisionDate = AdhUtil.deepPluck(
            AdhProcess.getStateData(process.data[SIWorkflowAssignment.nick], "result"), ["start_date"]);
        var proposalDecisionDate = AdhUtil.deepPluck(
            AdhProcess.getStateData(proposal.data[SIWorkflowAssignment.nick], proposalState), ["start_date"]);

        return (processDecisionDate === proposalDecisionDate) ? "current" : "archive";
    }
};


export var registerRoutes = (
    processType : string = "",
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider
        .default(RIS1Process, "", processType, context, {
            space: "content",
            landingPage: "true"
        })
        .default(RIS1Process, "current", processType, context, {
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
                            var processState = resource.data[SIWorkflowAssignment.nick].workflow_state;
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
                    commentableUrl: version.path,
                    commentCloseUrl: version.path,
                    meeting: getMeeting(item, process)
                };
            };
        });
};


export var moduleName = "adhS1Workbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhComment.moduleName,
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
        .directive("adhS1Landing", ["adhConfig", s1LandingDirective])
        .directive("adhS1CurrentColumn", ["adhConfig", "adhHttp", s1CurrentColumnDirective])
        .directive("adhS1NextColumn", ["adhConfig", "adhHttp", s1NextColumnDirective])
        .directive("adhS1ArchiveColumn", ["adhConfig", "adhHttp", s1ArchiveColumnDirective])
        .directive("adhS1ProposalDetailColumn", ["adhConfig", "adhPermissions", s1ProposalDetailColumnDirective])
        .directive("adhS1ProposalCreateColumn", ["adhConfig", s1ProposalCreateColumnDirective])
        .directive("adhS1ProposalEditColumn", ["adhConfig", s1ProposalEditColumnDirective]);
};
