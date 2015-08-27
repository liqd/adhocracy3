/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAngularHelpers = require("../../AngularHelpers/AngularHelpers");
import AdhBadge = require("../../Badge/Badge");
import AdhConfig = require("../../Config/Config");
import AdhHttp = require("../../Http/Http");
import AdhPermissions = require("../../Permissions/Permissions");
import AdhPreliminaryNames = require("../../PreliminaryNames/PreliminaryNames");
import AdhRate = require("../../Rate/Rate");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../TopLevelState/TopLevelState");
import AdhUtil = require("../../Util/Util");

import RICommentVersion = require("../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIProposal = require("../../../Resources_/adhocracy_s1/resources/s1/IProposal");
import RIProposalVersion = require("../../../Resources_/adhocracy_s1/resources/s1/IProposalVersion");
import SICommentable = require("../../../Resources_/adhocracy_core/sheets/comment/ICommentable");
import SIDescription = require("../../../Resources_/adhocracy_core/sheets/description/IDescription");
import SIMetadata = require("../../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIPool = require("../../../Resources_/adhocracy_core/sheets/pool/IPool");
import SIRateable = require("../../../Resources_/adhocracy_core/sheets/rate/IRateable");
import SITitle = require("../../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIVersionable = require("../../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/S1/Proposal";


interface IScope extends angular.IScope {
    path : string;
    resource : RIProposalVersion;
    selectedState? : string;
    data : {
        title : string;
        description : string;
        rateCount : number;
        creator : string;
        creationDate : string;
        commentCount : number;
        assignments : AdhBadge.IBadge[];
    };
}

interface IFormScope extends IScope {
    poolPath : string;
    errors : AdhHttp.IBackendErrorItem[];
    showError : Function;
    submit : Function;
    cancel : Function;
    S1ProposalForm : angular.IFormController;
}


var bindPath = (
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges,
    $q : angular.IQService
) => (
    scope : IScope,
    pathKey : string = "path"
) : void => {
    var getCommentCount = (resource) => {
        var commentableSheet : SICommentable.Sheet = resource.data[SICommentable.nick];

        return adhHttp.get(commentableSheet.post_pool, {
            content_type: RICommentVersion.content_type,
            depth: "all",
            tag: "LAST",
            count: true
        }).then((pool) => {
            return pool.data[SIPool.nick].count;
        });
    };

    scope.$watch(pathKey, (value : string) => {
        if (value) {
            // get resource
            adhHttp.get(value).then((resource : RIProposalVersion) => {
                scope.resource = resource;

                var titleSheet : SITitle.Sheet = resource.data[SITitle.nick];
                var descriptionSheet : SIDescription.Sheet = resource.data[SIDescription.nick];
                var metadataSheet : SIMetadata.Sheet = resource.data[SIMetadata.nick];
                var rateableSheet : SIRateable.Sheet = resource.data[SIRateable.nick];

                $q.all([
                    getCommentCount(resource),
                    adhGetBadges(resource),
                    adhRate.fetchAggregatedRates(rateableSheet.post_pool, resource.path)
                ]).then((args) => {
                    var commentCount = args[0];
                    var badgeAssignments = args[1];
                    // FIXME: an adapter should take care of this
                    var ratesPro = args[2]["1"] || 0;
                    var ratesContra = args[2]["-1"] || 0;

                    scope.data = {
                        title: titleSheet.title,
                        description: descriptionSheet.description,
                        rateCount: ratesPro - ratesContra,
                        creator: metadataSheet.creator,
                        creationDate: metadataSheet.item_creation_date,
                        commentCount: commentCount,
                        assignments: badgeAssignments
                    };
                });
            });
        }
        adhPermissions.bindScope(scope, () => scope[pathKey]);
    });
};

var fill = (
    scope : IScope,
    proposalVersion
) : void => {
    proposalVersion.data[SITitle.nick] = new SITitle.Sheet({
        title: scope.data.title
    });
    proposalVersion.data[SIDescription.nick] = new SIDescription.Sheet({
        description: scope.data.description
    });
};

var postCreate = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    poolPath : string
) => {
    var proposal = new RIProposal({preliminaryNames: adhPreliminaryNames});
    proposal.parent = poolPath;
    var proposalVersion = new RIProposalVersion({preliminaryNames: adhPreliminaryNames});

    proposalVersion.parent = proposal.path;
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [proposal.first_version_path]
    });
    fill(scope, proposalVersion);

    return adhHttp.deepPost([proposal, proposalVersion]);
};

var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    oldVersion : RIProposalVersion
) => {
    var proposalVersion = new RIProposalVersion({preliminaryNames: adhPreliminaryNames});
    proposalVersion.parent = AdhUtil.parentPath(oldVersion.path);
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [oldVersion.path]
    });
    fill(scope, proposalVersion);

    return adhHttp.deepPost([proposalVersion]);
};


export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(scope);
        }
    };
};

export var listItemDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(scope);
            scope.$on("$destroy", adhTopLevelState.on("proposalUrl", (proposalVersionUrl) => {
                if (!proposalVersionUrl) {
                    scope.selectedState = "";
                } else if (proposalVersionUrl === scope.path) {
                    scope.selectedState = "is-selected";
                } else {
                    scope.selectedState = "is-not-selected";
                }
            }));
        }
    };
};

export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid,
    adhResourceUrlFilter,
    $location : angular.ILocationService
) => {
    return {
        restrict: "E",
        scope: {
            poolPath: "@"
        },
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.data = <any>{};
            scope.showError = adhShowError;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.S1ProposalForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.poolPath)
                        .then((result) => {
                            $location.url(adhResourceUrlFilter(AdhUtil.parentPath(result[1].path)));
                        });
                });
            };

            scope.cancel = () => {
                var fallback = adhResourceUrlFilter(scope.poolPath);
                adhTopLevelState.goToCameFrom(fallback);
            };
        }
    };
};

export var editDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhRate : AdhRate.Service,
    adhResourceUrlFilter,
    adhShowError,
    adhSubmitIfValid,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges,
    $location : angular.ILocationService,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(scope);

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.S1ProposalForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.resource)
                        .then((result) => {
                            $location.url(adhResourceUrlFilter(AdhUtil.parentPath(result[0].path)));
                    });
                });
            };

            scope.cancel = () => {
                var fallback = adhResourceUrlFilter(AdhUtil.parentPath(scope.path));
                adhTopLevelState.goToCameFrom(fallback);
            };
        }
    };
};

export var listingDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            facets: "=?",
            update: "=?",
            sort: "=?",
            state: "@?",
            creator: "@?"
        },
        link: (scope) => {
            scope.contentType = RIProposalVersion.content_type;
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.params = {};

            if (scope.creator) {
                scope.params.creator = scope.creator.replace(adhConfig.rest_url, "").replace(/\/+$/, "");
                // processUrl is "/" in user space
                scope.params.depth = "all";
            }
            if (scope.state) {
                scope.params.workflow_state = scope.state;
            }
        }
    };
};


export var moduleName = "adhS1Proposal";

export var register = (angular) => {
    angular.module(moduleName, [
        AdhAngularHelpers.moduleName,
        AdhBadge.moduleName,
        AdhHttp.moduleName,
        AdhPermissions.moduleName,
        AdhPreliminaryNames.moduleName,
        AdhRate.moduleName,
        AdhResourceArea.moduleName,
        AdhTopLevelState.moduleName
    ])
    .directive("adhS1ProposalDetail", [
        "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", detailDirective])
    .directive("adhS1ProposalListItem", [
        "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", "$q", listItemDirective])
    .directive("adhS1ProposalCreate", [
        "adhConfig",
        "adhHttp",
        "adhPreliminaryNames",
        "adhTopLevelState",
        "adhShowError",
        "adhSubmitIfValid",
        "adhResourceUrlFilter",
        "$location",
        createDirective
    ])
    .directive("adhS1ProposalEdit", [
        "adhConfig",
        "adhHttp",
        "adhPermissions",
        "adhPreliminaryNames",
        "adhRate",
        "adhResourceUrlFilter",
        "adhShowError",
        "adhSubmitIfValid",
        "adhTopLevelState",
        "adhGetBadges",
        "$location",
        "$q",
        editDirective
    ])
    .directive("adhS1ProposalListing", ["adhConfig", "adhTopLevelState", listingDirective]);
};
