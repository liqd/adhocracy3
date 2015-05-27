/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAbuse = require("../../../Abuse/Abuse");
import AdhConfig = require("../../../Config/Config");
import AdhHttp = require("../../../Http/Http");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhProcess = require("../../../Process/Process");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUtil = require("../../../Util/Util");
import AdhPermissions = require("../../../Permissions/Permissions");

import AdhMeinBerlinKiezkassenProcess = require("../Process/Process");
import AdhMeinBerlinKiezkassenProposal = require("../Proposal/Proposal");

import RIComment = require("../../../../Resources_/adhocracy_core/resources/comment/IComment");
import RICommentVersion = require("../../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");
import RIProposal = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIComment = require("../../../../Resources_/adhocracy_core/sheets/comment/IComment");
import SIKiezkassenWorkflow = require("../../../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IWorkflowAssignment");

var pkgLocation = "/MeinBerlin/Kiezkassen/Workbench";


export var meinBerlinWorkbenchDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("contentType", scope));

            scope.views = {
                process: "default",
                proposal: "default",
                comment: "default"
            };

            scope.$watchGroup(["contentType", "view"], (values) => {
                console.log(values);
                var contentType = values[0];
                var view = values[1];

                if (contentType === RIKiezkassenProcess.content_type) {
                    scope.views.process = view;
                } else {
                    scope.views.process = "default";
                }

                if (contentType === RIProposal.content_type || contentType === RIProposalVersion.content_type) {
                    scope.views.proposal = view;
                } else {
                    scope.views.proposal = "default";
                }
            });

            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    adhHttp.get(processUrl).then((resource) => {
                        scope.currentPhase = resource.data[SIKiezkassenWorkflow.nick].workflow_state;
                    });
                }
            });
        }

    };
};

export var commentColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["proposalUrl", "commentableUrl"]);
        }
    };
};

export var kiezkassenProposalDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
            adhPermissions.bindScope(scope, () => scope.proposalUrl && AdhUtil.parentPath(scope.proposalUrl), "proposalItemOptions");
        }
    };
};

export var kiezkassenProposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
        }
    };
};

export var kiezkassenProposalEditColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenProposalEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
        }
    };
};

export var kiezkassenDetailColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.shared = column.$scope.shared;
            scope.showMap = (isShowMap) => {
                scope.shared.isShowMap = isShowMap;
            };
        }
    };
};

export var kiezkassenDetailAnnounceColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    var directive = kiezkassenDetailColumnDirective(adhConfig);
    directive.templateUrl = adhConfig.pkg_path + pkgLocation + "/KiezkassenDetailAnnounceColumn.html";
    return directive;
};

export var kiezkassenEditColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
        }
    };
};

export var moduleName = "adhMeinBerlinWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuse.moduleName,
            AdhHttp.moduleName,
            AdhMeinBerlinKiezkassenProcess.moduleName,
            AdhMeinBerlinKiezkassenProposal.moduleName,
            AdhMovingColumns.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RIKiezkassenProcess, "", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .default(RIKiezkassenProcess, "edit", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .specific(RIKiezkassenProcess, "edit", RIKiezkassenProcess.content_type, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (resource : RIKiezkassenProcess) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.PUT) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    }])
                .default(RIKiezkassenProcess, "create_proposal", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIKiezkassenProcess, "create_proposal", RIKiezkassenProcess.content_type, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (resource : RIKiezkassenProcess) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "edit", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "edit", RIKiezkassenProcess.content_type, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (item : RIProposal, version : RIProposalVersion) => {
                        return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {
                                    proposalUrl: version.path
                                };
                            }
                        });
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "", RIKiezkassenProcess.content_type, "", [
                    () => (item : RIProposal, version : RIProposalVersion) => {
                        return {
                            proposalUrl: version.path
                        };
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "comments", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "comments", RIKiezkassenProcess.content_type, "", [
                    () => (item : RIProposal, version : RIProposalVersion) => {
                        return {
                            commentableUrl: version.path,
                            proposalUrl: version.path
                        };
                    }])
                .defaultVersionable(RIComment, RICommentVersion, "", RIKiezkassenProcess.content_type, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIComment, RICommentVersion, "", RIKiezkassenProcess.content_type, "", ["adhHttp", "$q", (
                    adhHttp : AdhHttp.Service<any>,
                    $q : angular.IQService
                ) => {
                    var getCommentableUrl = (resource) : angular.IPromise<any> => {
                        if (resource.content_type !== RICommentVersion.content_type) {
                            return $q.when(resource);
                        } else {
                            var url = resource.data[SIComment.nick].refers_to;
                            return adhHttp.get(url).then(getCommentableUrl);
                        }
                    };

                    return (item : RIComment, version : RICommentVersion) => {
                        return getCommentableUrl(version).then((commentable) => {
                            return {
                                commentableUrl: commentable.path,
                                proposalUrl: commentable.path
                            };
                        });
                    };
                }]);
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIKiezkassenProcess.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mein-berlin-workbench></adh-mein-berlin-workbench>");
            }];
        }])
        .directive("adhMeinBerlinWorkbench", ["adhTopLevelState", "adhConfig", "adhHttp", meinBerlinWorkbenchDirective])
        .directive("adhCommentColumn", ["adhConfig", commentColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalDetailColumn", ["adhConfig", "adhPermissions", kiezkassenProposalDetailColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalCreateColumn", ["adhConfig", kiezkassenProposalCreateColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalEditColumn", ["adhConfig", kiezkassenProposalEditColumnDirective])
        .directive("adhMeinBerlinKiezkassenDetailColumn", ["adhConfig", kiezkassenDetailColumnDirective])
        .directive("adhMeinBerlinKiezkassenDetailAnnounceColumn", ["adhConfig", kiezkassenDetailAnnounceColumnDirective])
        .directive("adhMeinBerlinKiezkassenEditColumn", ["adhConfig", kiezkassenEditColumnDirective]);
};
