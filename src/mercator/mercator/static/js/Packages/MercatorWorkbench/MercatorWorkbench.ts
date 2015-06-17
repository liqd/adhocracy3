/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAbuse = require("../Abuse/Abuse");
import AdhComment = require("../Comment/Comment");
import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhListing = require("../Listing/Listing");
import AdhMercatorProposal = require("../MercatorProposal/MercatorProposal");
import AdhMovingColumns = require("../MovingColumns/MovingColumns");
import AdhPermissions = require("../Permissions/Permissions");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUser = require("../User/User");
import AdhUtil = require("../Util/Util");

import SIMercatorWorkflow = require("../../Resources_/adhocracy_mercator/sheets/mercator/IWorkflowAssignment");
import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIMercatorProposalVersion = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposalVersion");
import RIProcess = require("../../Resources_/adhocracy_mercator/resources/mercator/IProcess");
import SIComment = require("../../Resources_/adhocracy_core/sheets/comment/IComment");

var pkgLocation = "/MercatorWorkbench";


export var mercatorWorkbenchDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorWorkbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
        }
    };
};


var bindRedirectsToScope = (scope, adhConfig, adhResourceUrlFilter, $location) => {
    scope.redirectAfterProposalCancel = (resourcePath : string) => {
        // FIXME: use adhTopLevelState.redirectToCameFrom
        $location.url(adhResourceUrlFilter(resourcePath));
    };
    scope.redirectAfterProposalSubmit = (result : {path : string }[]) => {
        var proposalVersionPath = result.slice(-1)[0].path;
        $location.url(adhResourceUrlFilter(proposalVersionPath));
    };
};


export var commentColumnDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["proposalUrl", "commentableUrl"]);
            scope.frontendOrderPredicate = (id) => id;
            scope.frontendOrderReverse = true;
        }
    };
};


export var mercatorProposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhResourceUrlFilter : (path : string) => string,
    $location : angular.ILocationService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["platformUrl"]);
            bindRedirectsToScope(scope, adhConfig, adhResourceUrlFilter, $location);
        }
    };
};


export var mercatorProposalDetailColumnDirective = (
    $window : Window,
    adhTopLevelState : AdhTopLevelState.Service,
    adhPermissions : AdhPermissions.Service,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["platformUrl", "proposalUrl"]);
            adhPermissions.bindScope(scope, () => scope.proposalUrl && AdhUtil.parentPath(scope.proposalUrl), "proposalItemOptions");

            scope.delete = () => {
                column.$broadcast("triggerDelete", scope.proposalUrl);
            };

            scope.print = () => {
                // only the focused column is printed
                adhTopLevelState.set("focus", 1);
                $window.print();
            };
        }
    };
};


export var mercatorProposalEditColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhResourceUrlFilter : (path : string) => string,
    $location : angular.ILocationService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["platformUrl", "proposalUrl"]);
            bindRedirectsToScope(scope, adhConfig, adhResourceUrlFilter, $location);
        }
    };
};


export var mercatorProposalListingColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalListingColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["platformUrl", "proposalUrl"]);
            scope.contentType = RIMercatorProposalVersion.content_type;

            var processUrl = adhTopLevelState.get("processUrl");
            adhHttp.get(processUrl).then((resource) => {
                var currentPhase = resource.data[SIMercatorWorkflow.nick].workflow_state;

                scope.shared.facets = [{
                    key: "mercator_location",
                    name: "TR__MERCATOR_PROPOSAL_LOCATION_LABEL",
                    items: [
                        {key: "specific", name: "TR__MERCATOR_PROPOSAL_SPECIFIC"},
                        {key: "online", name: "TR__ONLINE"},
                        {key: "linked_to_ruhr", name: "TR__MERCATOR_PROPOSAL_LOCATION_LINKAGE_TO_RUHR"}
                    ]
                }, {
                    key: "mercator_requested_funding",
                    name: "TR__MERCATOR_PROPOSAL_REQUESTED_FUNDING",
                    items: [
                        {key: "5000", name: "0 - 5000 €"},
                        {key: "10000", name: "5000 - 10000 €"},
                        {key: "20000", name: "10000 - 20000 €"},
                        {key: "50000", name: "20000 - 50000 €"}
                    ]
                }];

                if (currentPhase === "result") {
                    scope.shared.facets.push({
                        key: "badge",
                        name: "TR__MERCATOR_BADGE_AWARDS_LABEL",
                        items: [
                            {key: "winning", name: "TR__MERCATOR_BADGE_WINNERS", enabled: true},
                            {key: "community", name: "TR__MERCATOR_BADGE_COMMUNITY_AWARD"}
                        ]
                    });
                }

                scope.shared.sort = "item_creation_date";
                scope.shared.reverse = true;
                scope.shared.setSort = (sort : string) => {
                    scope.shared.sort = sort;
                };
                scope.initialLimit = 50;
            });
        }
    };
};


export var moduleName = "adhMercatorWorkbench";

export var register = (angular) => {
    var processType = RIProcess.content_type;

    angular
        .module(moduleName, [
            AdhAbuse.moduleName,
            AdhComment.moduleName,
            AdhHttp.moduleName,
            AdhListing.moduleName,
            AdhMercatorProposal.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName,
            AdhUser.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RICommentVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RICommentVersion, "", processType, "", ["adhHttp", "$q", (
                    adhHttp : AdhHttp.Service<any>,
                    $q : angular.IQService
                ) => (resource : RICommentVersion) => {
                    var specifics = {};
                    specifics["commentUrl"] = resource.path;

                    var getCommentableUrl = (resource) : angular.IPromise<any> => {
                        if (resource.content_type !== RICommentVersion.content_type) {
                            return $q.when(resource);
                        } else {
                            var url = resource.data[SIComment.nick].refers_to;
                            return adhHttp.get(url).then(getCommentableUrl);
                        }
                    };

                    return getCommentableUrl(resource).then((commentable) => {
                        specifics["commentableUrl"] = commentable.path;

                        if (commentable.content_type === RIMercatorProposalVersion.content_type) {
                            specifics["proposalUrl"] = specifics["commentableUrl"];
                        } else {
                            var subResourceUrl = AdhUtil.parentPath(specifics["commentableUrl"]);
                            var proposalItemUrl = AdhUtil.parentPath(subResourceUrl);
                            return adhHttp.getNewestVersionPathNoFork(proposalItemUrl).then((proposalUrl) => {
                                specifics["proposalUrl"] = proposalUrl;
                            });
                        }
                    })
                    .then(() => specifics);
                }])
                .default(RIProcess, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    proposalUrl: "",  // not used by default, but should be overridable
                    focus: "0"
                })
                .default(RIProcess, "create_proposal", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .specific(RIProcess, "create_proposal", processType, "", ["adhHttp",
                    (adhHttp : AdhHttp.Service<any>) => {
                        return (resource : RIProcess) => {
                            return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                                if (!options.POST) {
                                    throw 401;
                                } else {
                                    return {};
                                }
                            });
                        };
                    }]
                );
        }])
        .config(["adhProcessProvider", (adhProcessProvider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mercator-workbench></adh-mercator-workbench>");
            }];
        }])
        .directive("adhMercatorWorkbench", ["adhConfig", "adhTopLevelState", mercatorWorkbenchDirective])
        .directive("adhCommentColumn", ["adhConfig", commentColumnDirective])
        .directive("adhMercatorProposalCreateColumn", [
            "adhConfig", "adhResourceUrlFilter", "$location", mercatorProposalCreateColumnDirective])
        .directive("adhMercatorProposalDetailColumn", [
            "$window", "adhTopLevelState", "adhPermissions", "adhConfig", mercatorProposalDetailColumnDirective])
        .directive("adhMercatorProposalEditColumn", [
            "adhConfig", "adhResourceUrlFilter", "$location", mercatorProposalEditColumnDirective])
        .directive("adhMercatorProposalListingColumn",
            ["adhConfig", "adhHttp", "adhTopLevelState", mercatorProposalListingColumnDirective]);
};
