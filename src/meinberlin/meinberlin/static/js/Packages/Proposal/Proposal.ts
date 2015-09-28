/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import * as AdhBadge from "../Badge/Badge";
import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhMapping from "../Mapping/Mapping";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";
import * as AdhRate from "../Rate/Rate";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUtil from "../Util/Util";

import RIBurgerhaushaltProposal from "../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProposal";
import RIBurgerhaushaltProposalVersion from "../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProposalVersion";
import RICommentVersion from "../../Resources_/adhocracy_core/resources/comment/ICommentVersion";
import RIGeoProposal from "../../Resources_/adhocracy_core/resources/proposal/IGeoProposal";
import RIGeoProposalVersion from "../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion";
import RIKiezkassenProposal from "../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal";
import RIKiezkassenProposalVersion from "../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion";
import * as SIBurgerhaushaltProposal from "../../Resources_/adhocracy_meinberlin/sheets/burgerhaushalt/IProposal";
import * as SICommentable from "../../Resources_/adhocracy_core/sheets/comment/ICommentable";
import * as SIDescription from "../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SIKiezkassenProposal from "../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IProposal";
import * as SILocationReference from "../../Resources_/adhocracy_core/sheets/geo/ILocationReference";
import * as SIMetadata from "../../Resources_/adhocracy_core/sheets/metadata/IMetadata";
import * as SIMultiPolygon from "../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon";
import * as SIPoint from "../../Resources_/adhocracy_core/sheets/geo/IPoint";
import * as SIPool from "../../Resources_/adhocracy_core/sheets/pool/IPool";
import * as SIRateable from "../../Resources_/adhocracy_core/sheets/rate/IRateable";
import * as SITitle from "../../Resources_/adhocracy_core/sheets/title/ITitle";
import * as SIVersionable from "../../Resources_/adhocracy_core/sheets/versions/IVersionable";

var pkgLocation = "/Proposal";


export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {
        title : string;
        detail : string;
        rateCount : number;
        creator : string;
        creationDate : string;
        commentCount : number;
        lng : number;
        lat : number;
        polygon: number[][];
        assignments : AdhBadge.IBadge[];

        budget? : number;
        creatorParticipate? : boolean;
        locationText? : string;
        address? : string;
    };
    selectedState? : string;
    isKiezkasse : boolean;
    isBurgerhaushalt : boolean;
    resource : any;
}

// FIXME: the following functions duplicate some of the adhResourceWidget functionality
// They are an experiment on how adhResourceWidget can be improved.  This duplication
// should be resolved at some point.
var bindPath = (
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges,
    $q : angular.IQService
) => (
    scope : IScope,
    pathKey : string = "path",
    isKiezkasse : boolean = false,
    isBurgerhaushalt : boolean = false
) : void => {
    var getPolygon = () => {
        var processUrl = adhTopLevelState.get("processUrl");

        return adhHttp.get(processUrl).then((process) => {
            var locationUrl = process.data[SILocationReference.nick]["location"];

            return adhHttp.get(locationUrl).then((location) => {
                return location.data[SIMultiPolygon.nick]["coordinates"][0][0];
            });
        });
    };

    var getCommentCount = (resource) : angular.IPromise<number> => {
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
            adhHttp.get(value).then((resource) => {
                scope.resource = resource;

                var titleSheet : SITitle.Sheet = resource.data[SITitle.nick];
                var descriptionSheet : SIDescription.Sheet = resource.data[SIDescription.nick];
                var pointSheet : SIPoint.Sheet = resource.data[SIPoint.nick];
                var metadataSheet : SIMetadata.Sheet = resource.data[SIMetadata.nick];
                var rateableSheet : SIRateable.Sheet = resource.data[SIRateable.nick];

                if (isKiezkasse) {
                    var kiezkassenSheet : SIKiezkassenProposal.Sheet = resource.data[SIKiezkassenProposal.nick];
                } else if (isBurgerhaushalt) {
                    var burgerhaushaltSheet : SIBurgerhaushaltProposal.Sheet = resource.data[SIBurgerhaushaltProposal.nick];
                }

                $q.all([
                    getCommentCount(resource),
                    adhRate.fetchAggregatedRates(rateableSheet.post_pool, resource.path),
                    getPolygon(),
                    adhGetBadges(resource)
                ]).then((args : any[]) => {
                    var commentCount = args[0];
                    var rates = args[1];
                    var polygon = args[2];
                    var assignments = args[3];

                    // FIXME: an adapter should take care of this
                    var ratesPro = rates["1"] || 0;
                    var ratesContra = rates["-1"] || 0;

                    scope.data = {
                        title: titleSheet.title,
                        detail: descriptionSheet.description,
                        rateCount: ratesPro - ratesContra,
                        creator: metadataSheet.creator,
                        creationDate: metadataSheet.item_creation_date,
                        commentCount: commentCount,
                        lng: pointSheet.coordinates[0],
                        lat: pointSheet.coordinates[1],
                        polygon: polygon,
                        assignments: assignments
                    };
                    if (isKiezkasse) {
                        scope.data.budget = kiezkassenSheet.budget;
                        scope.data.address = kiezkassenSheet.address;
                        scope.data.creatorParticipate = kiezkassenSheet.creator_participate;
                        scope.data.locationText = kiezkassenSheet.location_text;
                    } else if (isBurgerhaushalt) {
                        scope.data.budget = burgerhaushaltSheet.budget;
                        scope.data.locationText = burgerhaushaltSheet.location_text;
                    }
                });
            });
        }
        adhPermissions.bindScope(scope, () => scope[pathKey]);
    });
};

var fill = (
    scope : IScope,
    proposalVersion,
    isKiezkasse : boolean = false,
    isBurgerhaushalt : boolean = false
) : void => {

    if (isKiezkasse) {
        proposalVersion.data[SIKiezkassenProposal.nick] = new SIKiezkassenProposal.Sheet({
            budget: scope.data.budget,
            creator_participate: scope.data.creatorParticipate,
            location_text: scope.data.locationText,
            address: scope.data.address
        });
    } else if (isBurgerhaushalt) {
        proposalVersion.data[SIBurgerhaushaltProposal.nick] = new SIBurgerhaushaltProposal.Sheet({
            budget: scope.data.budget,
            location_text: scope.data.locationText
        });
    }
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
    poolPath : string,
    isKiezkasse : boolean = false,
    isBurgerhaushalt : boolean = false
) => {
    var proposalClass = RIGeoProposal;
    var proposalVersionClass = RIGeoProposalVersion;

    if (isKiezkasse) {
        proposalClass = RIKiezkassenProposal;
        proposalVersionClass = RIKiezkassenProposalVersion;
    } else if (isBurgerhaushalt) {
        proposalClass = RIBurgerhaushaltProposal;
        proposalVersionClass = RIBurgerhaushaltProposalVersion;
    }

    var proposal = new proposalClass({preliminaryNames: adhPreliminaryNames});
    proposal.parent = poolPath;
    var proposalVersion = new proposalVersionClass({preliminaryNames: adhPreliminaryNames});

    proposalVersion.parent = proposal.path;
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [proposal.first_version_path]
    });
    fill(scope, proposalVersion, isKiezkasse, isBurgerhaushalt);

    return adhHttp.deepPost([proposal, proposalVersion]);
};

var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    oldVersion,
    isKiezkasse : boolean = false,
    isBurgerhaushalt : boolean = false
) => {
    var proposalVersionClass = RIGeoProposalVersion;

    if (isKiezkasse) {
        proposalVersionClass = RIKiezkassenProposalVersion;
    } else if (isBurgerhaushalt) {
        proposalVersionClass = RIBurgerhaushaltProposalVersion;
    }

    var proposalVersion = new proposalVersionClass({preliminaryNames: adhPreliminaryNames});
    proposalVersion.parent = AdhUtil.parentPath(oldVersion.path);
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [oldVersion.path]
    });
    fill(scope, proposalVersion, isKiezkasse, isBurgerhaushalt);

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
            path: "@",
            isKiezkasse: "=?",
            isBurgerhaushalt: "=?"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(
                scope, undefined, scope.isKiezkasse, scope.isBurgerhaushalt);
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
            path: "@",
            isKiezkasse: "=?",
            isBurgerhaushalt: "=?"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(
                scope, undefined, scope.isKiezkasse, scope.isBurgerhaushalt);
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
    adhGetBadges : AdhBadge.IGetBadges,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        require: "^adhMapListingInternal",
        scope: {
            path: "@",
            isKiezkasse: "=?",
            isBurgerhaushalt: "=?"
        },
        link: (scope : IScope, element, attrs, mapListing : AdhMapping.MapListingController) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(
                scope, undefined, scope.isKiezkasse, scope.isBurgerhaushalt);

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
        scope: {
            isKiezkasse: "=?",
            isBurgerhaushalt: "=?"
        },
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
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, processUrl, scope.isKiezkasse, scope.isBurgerhaushalt)
                        .then((result) => {
                            $location.url(adhResourceUrlFilter(AdhUtil.parentPath(result[1].path)));
                        });
                });
            };

            scope.cancel = () => {
                var fallback = adhResourceUrlFilter(scope.processUrl);
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
            path: "@",
            isKiezkasse: "=?",
            isBurgerhaushalt: "=?"
        },
        link: (scope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;
            scope.create = false;
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges, $q)(
                scope, undefined, scope.isKiezkasse, scope.isBurgerhaushalt);

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.resource, scope.isKiezkasse, scope.isBurgerhaushalt)
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
