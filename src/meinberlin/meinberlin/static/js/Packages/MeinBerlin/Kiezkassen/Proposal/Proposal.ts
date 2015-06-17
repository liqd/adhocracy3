/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import _ = require("lodash");

import AdhAngularHelpers = require("../../../AngularHelpers/AngularHelpers");
import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhHttp = require("../../../Http/Http");
import AdhMapping = require("../../../Mapping/Mapping");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhPreliminaryNames = require("../../../PreliminaryNames/PreliminaryNames");
import AdhRate = require("../../../Rate/Rate");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUtil = require("../../../Util/Util");

import RIBadgeAssignment = require("../../../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment");
import RICommentVersion = require("../../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIProposal = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIBadgeable = require("../../../../Resources_/adhocracy_core/sheets/badge/IBadgeable");
import SIBadgeAssignment = require("../../../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment");
import SIMetadata = require("../../../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIName = require("../../../../Resources_/adhocracy_core/sheets/name/IName");
import SIPoint = require("../../../../Resources_/adhocracy_core/sheets/geo/IPoint");
import SIPool = require("../../../../Resources_/adhocracy_core/sheets/pool/IPool");
import SIProposal = require("../../../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IProposal");
import SIRateable = require("../../../../Resources_/adhocracy_core/sheets/rate/IRateable");
import SIVersionable = require("../../../../Resources_/adhocracy_core/sheets/versions/IVersionable");
import SITitle = require("../../../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIDescription = require("../../../../Resources_/adhocracy_core/sheets/description/IDescription");
import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");

var pkgLocation = "/MeinBerlin/Kiezkassen/Proposal";


export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {
        title : string;
        budget : number;
        detail : string;
        creatorParticipate : boolean;
        locationText : string;
        address : string;
        creator : string;
        creationDate : string;
        commentCount : number;
        lng : number;
        lat : number;
        polygon: number[][];
        assignments : BadgeAssignment[];
    };
    selectedState? : string;
    resource: RIProposalVersion;
}

export class BadgeAssignment {
    constructor(
        private title : string,
        private description : string,
        private name : string
    ) {}
}

var getBadges = (
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService
) => (proposal : RIProposalVersion) : angular.IPromise<BadgeAssignment[]> => {
    return $q.all(_.map(proposal.data[SIBadgeable.nick].assignments, (assignmentPath : string) => {
        return adhHttp.get(assignmentPath).then((assignment : RIBadgeAssignment) => {
            var description = assignment.data[SIDescription.nick].description;
            return adhHttp.get(assignment.data[SIBadgeAssignment.nick].badge).then((badge) => {
                var title = badge.data[SITitle.nick].title;
                var name = badge.data[SIName.nick].name;
                return new BadgeAssignment(title, description, name);
            });
        });
    }));
};

// FIXME: the following functions duplicate some of the adhResourceWidget functionality
// They are an experiment on how adhResourceWidget can be improved.  This duplication
// should be resolved at some point.
var bindPath = (
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    $q : angular.IQService
) => (
    scope : IScope,
    pathKey : string = "path"
) : void => {
    scope.$watch(pathKey, (value : string) => {
        if (value) {

            // FIXME: Load resources in parallel (use $q.all)
            adhHttp.get(AdhUtil.parentPath(value), {
                content_type: RICommentVersion.content_type,
                depth: "all",
                tag: "LAST",
                count: true
            }).then((pool) => {
                adhHttp.get(value).then((resource : RIProposalVersion) => {

                    scope.resource = resource;

                    var titleSheet : SITitle.Sheet = resource.data[SITitle.nick];
                    var descriptionSheet : SIDescription.Sheet = resource.data[SIDescription.nick];
                    var mainSheet : SIProposal.Sheet = resource.data[SIProposal.nick];
                    var pointSheet : SIPoint.Sheet = resource.data[SIPoint.nick];
                    var metadataSheet : SIMetadata.Sheet = resource.data[SIMetadata.nick];
                    var rateableSheet : SIRateable.Sheet = resource.data[SIRateable.nick];
                    var poolSheet = pool.data[SIPool.nick];

                    adhRate.fetchAggregatedRates(rateableSheet.post_pool, resource.path).then((rates) => {
                        // FIXME: an adapter should take care of this
                        var ratesPro = rates["1"] || 0;
                        var ratesContra = rates["-1"] || 0;

                        var processUrl = adhTopLevelState.get("processUrl");
                        adhHttp.get(processUrl).then((process) => {
                            var locationUrl = process.data[SILocationReference.nick]["location"];
                            adhHttp.get(locationUrl).then((location) => {
                                var polygon = location.data[SIMultiPolygon.nick]["coordinates"][0][0];
                                getBadges(adhHttp, $q)(resource).then((assignments) => {
                                    scope.data = {
                                        title: titleSheet.title,
                                        budget: mainSheet.budget,
                                        detail: descriptionSheet.description,
                                        creatorParticipate: mainSheet.creator_participate,
                                        address: mainSheet.address,
                                        rateCount: ratesPro - ratesContra,
                                        locationText: mainSheet.location_text,
                                        adlocationText: mainSheet.location_text,
                                        creator: metadataSheet.creator,
                                        creationDate: metadataSheet.item_creation_date,
                                        commentCount: poolSheet.count,
                                        lng: pointSheet.coordinates[0],
                                        lat: pointSheet.coordinates[1],
                                        polygon: polygon,
                                        assignments: assignments
                                    };
                                });
                            });
                        });
                    });
                });
            });
        }
        adhPermissions.bindScope(scope, () => scope[pathKey]);
    });
};

var fill = (
    scope : IScope,
    proposalVersion : RIProposalVersion
) : void => {
    proposalVersion.data[SIProposal.nick] = new SIProposal.Sheet({
        budget: scope.data.budget,
        detail: scope.data.detail,
        creator_participate: scope.data.creatorParticipate,
        location_text: scope.data.locationText,
        address: scope.data.address
    });
    proposalVersion.data[SITitle.nick] = new SITitle.Sheet({
        title: scope.data.title
    });
    proposalVersion.data[SIDescription.nick] = new SIDescription.Sheet({
        description: scope.data.detail
    });
    if (scope.data.lng && scope.data.lat) {
        proposalVersion.data[SIPoint.nick] = new SIPoint.Sheet({
            coordinates: [scope.data.lng, scope.data.lat]
        });
    }
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
    proposal.data[SIName.nick] = new SIName.Sheet({
        name: AdhUtil.normalizeName(scope.data.title)
    });

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
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, $q)(scope);
        }
    };
};

export var listItemDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, $q)(scope);
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

export var mapListItemDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        require: "^adhMapListingInternal",
        scope: {
            path: "@"
        },
        link: (scope : IScope, element, attrs, mapListing : AdhMapping.MapListingController) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, $q)(scope);

            var unregister = scope.$watchGroup(["data.lat", "data.lng"], (values : number[]) => {
                if (typeof values[0] !== "undefined" && typeof values[1] !== "undefined") {
                    scope.$on("$destroy", mapListing.registerListItem(scope.path, values[0], values[1]));
                    unregister();
                }
            });

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
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope, element) => {
            scope.errors = [];
            scope.data = {};
            scope.create = true;
            scope.showError = adhShowError;

            scope.data.lat = undefined;
            scope.data.lng = undefined;

            var processUrl = adhTopLevelState.get("processUrl");
            adhHttp.get(processUrl).then((process) => {
                var locationUrl = process.data[SILocationReference.nick]["location"];
                adhHttp.get(locationUrl).then((location) => {
                    var polygon = location.data[SIMultiPolygon.nick]["coordinates"][0][0];
                    scope.data.polygon =  polygon;
                });
            });

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, processUrl)
                        .then((result) => {
                            $location.url(adhResourceUrlFilter(AdhUtil.parentPath(result[1].path)));
                        });
                });
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
    $location : angular.ILocationService,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;
            scope.create = false;
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, $q)(scope);
            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.resource)
                        .then((result) => {
                            $location.url(adhResourceUrlFilter(AdhUtil.parentPath(result[0].path)));
                    });
                });
            };
        }
    };
};

export var meinBerlinProposalFormController = ($scope, $element, $window) => {
    console.log($scope);
};


export var moduleName = "adhMeinBerlinKiezkassenProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhEmbed.moduleName,
            AdhHttp.moduleName,
            AdhMapping.moduleName,
            AdhPermissions.moduleName,
            AdhRate.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-kiezkassen-proposal-detail");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-kiezkassen-proposal-list-item");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-kiezkassen-proposal-create");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-kiezkassen-proposal-edit");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-kiezkassen-proposal-list");
        }])
        .directive("adhMeinBerlinKiezkassenProposalDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "$q", detailDirective])
        .directive("adhMeinBerlinKiezkassenProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "$q", listItemDirective])
        .directive("adhMeinBerlinKiezkassenProposalMapListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "$q", mapListItemDirective])
        .directive("adhMeinBerlinKiezkassenProposalCreate", [
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            "$location",
            "$q",
            createDirective
        ])
        .directive("adhMeinBerlinKiezkassenProposalEdit", [
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhPreliminaryNames",
            "adhRate",
            "adhResourceUrlFilter",
            "adhShowError",
            "adhSubmitIfValid",
            "adhTopLevelState",
            "$location",
            "$q",
            editDirective
        ])
        .controller("meinBerlinKiezkassenProposalFormController", [meinBerlinProposalFormController]);
};
