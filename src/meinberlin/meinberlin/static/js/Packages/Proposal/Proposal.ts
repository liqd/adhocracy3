/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhBadge = require("../Badge/Badge");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhMapping = require("../Mapping/Mapping");
import AdhPermissions = require("../Permissions/Permissions");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhRate = require("../Rate/Rate");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIGeoProposal = require("../../Resources_/adhocracy_core/resources/proposal/IGeoProposal");
import RIGeoProposalVersion = require("../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion");
import RIKiezkassenProposal = require("../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal");
import RIKiezkassenProposalVersion = require("../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIDescription = require("../../Resources_/adhocracy_core/sheets/description/IDescription");
import SIKiezkassenProposal = require("../../Resources_/adhocracy_meinberlin/sheets/kiezkassen/IProposal");
import SILocationReference = require("../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMetadata = require("../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIMultiPolygon = require("../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");
import SIPoint = require("../../Resources_/adhocracy_core/sheets/geo/IPoint");
import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");
import SIRateable = require("../../Resources_/adhocracy_core/sheets/rate/IRateable");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/Proposal";


export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {
        title : string;
        detail : string;
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
    adhGetBadges : AdhBadge.IGetBadges
) => (
    scope : IScope,
    pathKey : string = "path",
    isKiezkasse : boolean = false
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
                adhHttp.get(value).then((resource) => {

                    scope.resource = resource;

                    var titleSheet : SITitle.Sheet = resource.data[SITitle.nick];
                    var descriptionSheet : SIDescription.Sheet = resource.data[SIDescription.nick];
                    if (isKiezkasse) {
                        var kiezkassenSheet : SIKiezkassenProposal.Sheet = resource.data[SIKiezkassenProposal.nick];
                    }
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
                                adhGetBadges(resource).then((assignments) => {
                                    scope.data = {
                                        title: titleSheet.title,
                                        detail: descriptionSheet.description,
                                        rateCount: ratesPro - ratesContra,
                                        creator: metadataSheet.creator,
                                        creationDate: metadataSheet.item_creation_date,
                                        commentCount: poolSheet.count,
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
                                    }
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
    proposalVersion,
    isKiezkasse : boolean = false
) : void => {

    if (isKiezkasse) {
        proposalVersion.data[SIKiezkassenProposal.nick] = new SIKiezkassenProposal.Sheet({
            budget: scope.data.budget,
            detail: scope.data.detail,
            creator_participate: scope.data.creatorParticipate,
            location_text: scope.data.locationText,
            address: scope.data.address
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
    isKiezkasse : boolean = false
) => {
    var proposalClass = isKiezkasse ? RIKiezkassenProposal : RIGeoProposal;
    var proposalVersionClass = isKiezkasse ? RIKiezkassenProposalVersion : RIGeoProposalVersion;

    var proposal = new proposalClass({preliminaryNames: adhPreliminaryNames});
    proposal.parent = poolPath;
    var proposalVersion = new proposalVersionClass({preliminaryNames: adhPreliminaryNames});

    proposalVersion.parent = proposal.path;
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [proposal.first_version_path]
    });
    fill(scope, proposalVersion, isKiezkasse);

    return adhHttp.deepPost([proposal, proposalVersion]);
};

var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    oldVersion,
    isKiezkasse : boolean = false
) => {
    var proposalVersionClass = isKiezkasse ? RIKiezkassenProposalVersion : RIGeoProposalVersion;

    var proposalVersion = new proposalVersionClass({preliminaryNames: adhPreliminaryNames});
    proposalVersion.parent = AdhUtil.parentPath(oldVersion.path);
    proposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [oldVersion.path]
    });
    fill(scope, proposalVersion, isKiezkasse);

    return adhHttp.deepPost([proposalVersion]);
};

export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@",
            isKiezkasse: "="
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges)(scope, undefined, scope.isKiezkasse);
        }
    };
};

export var listItemDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhRate : AdhRate.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadges
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@",
            isKiezkasse: "="
        },
        link: (scope : IScope) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges)(scope, undefined, scope.isKiezkasse);
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
    adhGetBadges : AdhBadge.IGetBadges
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        require: "^adhMapListingInternal",
        scope: {
            path: "@",
            isKiezkasse: "="
        },
        link: (scope : IScope, element, attrs, mapListing : AdhMapping.MapListingController) => {
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges)(scope, undefined, scope.isKiezkasse);

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
            isKiezkasse: "="
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
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, processUrl, scope.isKiezkasse)
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
    $location : angular.ILocationService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@",
            isKiezkasse: "="
        },
        link: (scope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;
            scope.create = false;
            bindPath(adhHttp, adhPermissions, adhRate, adhTopLevelState, adhGetBadges)(scope, undefined, scope.isKiezkasse);

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinBerlinProposalForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.resource, scope.isKiezkasse)
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


export var moduleName = "adhMeinBerlinProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhBadge.moduleName,
            AdhEmbed.moduleName,
            AdhHttp.moduleName,
            AdhMapping.moduleName,
            AdhPermissions.moduleName,
            AdhRate.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-detail");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-list-item");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-create");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-edit");
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-proposal-list");
        }])
        .directive("adhMeinBerlinProposalDetail", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", detailDirective])
        .directive("adhMeinBerlinProposalListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", listItemDirective])
        .directive("adhMeinBerlinProposalMapListItem", [
            "adhConfig", "adhHttp", "adhPermissions", "adhRate", "adhTopLevelState", "adhGetBadges", mapListItemDirective])
        .directive("adhMeinBerlinProposalCreate", [
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
        .directive("adhMeinBerlinProposalEdit", [
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
            editDirective
        ]);
};
