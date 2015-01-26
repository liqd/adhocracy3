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
import AdhUserViews = require("../User/Views");
import AdhUtil = require("../Util/Util");

import RIPoolWithAssets = require("../../Resources_/adhocracy_core/resources/asset/IPoolWithAssets");
import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIMercatorProposalVersion = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposalVersion");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");
import SIComment = require("../../Resources_/adhocracy_core/sheets/comment/IComment");

var pkgLocation = "/MercatorWorkbench";


export var mercatorWorkbenchDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorWorkbench.html"
    };
};


var bindRedirectsToScope = (scope, adhConfig, $location) => {
    // FIXME: use dependency injection instead
    var adhResourceUrl = AdhResourceArea.resourceUrl(adhConfig);

    scope.redirectAfterProposalCancel = (resourcePath : string) => {
        // FIXME: use adhTopLevelState.redirectToCameFrom
        $location.url(adhResourceUrl(resourcePath));
    };
    scope.redirectAfterProposalSubmit = (result : {path : string }[]) => {
        var proposalVersionPath = result.slice(-1)[0].path;
        $location.url(adhResourceUrl(proposalVersionPath));
    };
};


export var commentColumnDirective = (adhTopLevelState : AdhTopLevelState.Service, adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("proposalUrl", scope);
            adhTopLevelState.bind("commentableUrl", scope);
        }
    };
};


export var mercatorProposalCreateColumnDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService,
    $location : ng.ILocationService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("platformUrl", scope);
            bindRedirectsToScope(scope, adhConfig, $location);
        }
    };
};


export var mercatorProposalDetailColumnDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhPermissions : AdhPermissions.Service,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("platformUrl", scope);
            adhTopLevelState.bind("proposalUrl", scope);
            adhPermissions.bindScope(scope, () => scope.proposalUrl && AdhUtil.parentPath(scope.proposalUrl), "proposalItemOptions");
        }
    };
};


export var mercatorProposalEditColumnDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService,
    $location : ng.ILocationService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("platformUrl", scope);
            adhTopLevelState.bind("proposalUrl", scope);
            bindRedirectsToScope(scope, adhConfig, $location);
        }
    };
};


export var mercatorProposalListingColumnDirective = (adhTopLevelState : AdhTopLevelState.Service, adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MercatorProposalListingColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("platformUrl", scope);
            adhTopLevelState.bind("proposalUrl", scope);
            scope.contentType = RIMercatorProposalVersion.content_type;
            scope.shared.facets = [{
                key: "mercator_location",
                name: "Location",
                items: [
                    {key: "specific", name: "Specific"},
                    {key: "online", name: "Online"},
                    {key: "linked_to_ruhr", name: "Linked to the Ruhr area"}
                ]
            }, {
                key: "mercator_requested_funding",
                name: "Requested funding",
                items: [
                    {key: "5000", name: "0 - 5000 €"},
                    {key: "10000", name: "5000 - 10000 €"},
                    {key: "20000", name: "10000 - 20000 €"},
                    {key: "50000", name: "20000 - 50000 €"}
                ]
            }];
            scope.shared.sort = "-rates";
        }
    };
};


export var userDetailColumnDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhPermissions : AdhPermissions.Service,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/UserDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("userUrl", scope);
            adhPermissions.bindScope(scope, adhConfig.rest_url + "/message_user", "messageOptions");
        }
    };
};


export var userListingColumnDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/UserListingColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            adhTopLevelState.bind("userUrl", scope);
        }
    };
};


export var moduleName = "adhMercatorWorkbench";

export var register = (angular) => {
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
            AdhUser.moduleName,
            AdhUserViews.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RICommentVersion.content_type, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RICommentVersion.content_type, "", ["adhHttp", "$q", (adhHttp : AdhHttp.Service<any>, $q : ng.IQService) =>
                                                              (resource : RICommentVersion) => {
                    var specifics = {};
                    specifics["commentUrl"] = resource.path;

                    var getCommentableUrl = (resource) : ng.IPromise<any> => {
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
                .default(RIUser.content_type, "", {
                    space: "user",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIUser.content_type, "", () => (resource : RIUser) => {
                    return {
                        userUrl: resource.path
                    };
                })
                .default(RIUsersService.content_type, "", {
                    space: "user",
                    movingColumns: "is-show-hide-hide",
                    userUrl: "",  // not used by default, but should be overridable
                    focus: "0"
                })
                .default(RIPoolWithAssets.content_type, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    proposalUrl: "",  // not used by default, but should be overridable
                    focus: "0"
                })
                .default(RIPoolWithAssets.content_type, "create_proposal", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .specific(RIPoolWithAssets.content_type, "create_proposal", ["adhHttp", (adhHttp : AdhHttp.Service<any>) => {
                    return (resource : RIPoolWithAssets) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    };
                }]);
        }])
        .directive("adhMercatorWorkbench", ["adhConfig", mercatorWorkbenchDirective])
        .directive("adhCommentColumn", ["adhTopLevelState", "adhConfig", commentColumnDirective])
        .directive("adhMercatorProposalCreateColumn", ["adhTopLevelState", "adhConfig", "$location", mercatorProposalCreateColumnDirective])
        .directive("adhMercatorProposalDetailColumn", ["adhTopLevelState", "adhPermissions", "adhConfig",
            mercatorProposalDetailColumnDirective])
        .directive("adhMercatorProposalEditColumn", ["adhTopLevelState", "adhConfig", "$location", mercatorProposalEditColumnDirective])
        .directive("adhMercatorProposalListingColumn", ["adhTopLevelState", "adhConfig", mercatorProposalListingColumnDirective])
        .directive("adhUserDetailColumn", ["adhTopLevelState", "adhPermissions", "adhConfig", userDetailColumnDirective])
        .directive("adhUserListingColumn", ["adhTopLevelState", "adhConfig", userListingColumnDirective]);
};
