/// <reference path="../../../../../lib2/types/angular.d.ts"/>
/// <reference path="../../../../../lib2/types/moment.d.ts"/>

import * as AdhBadge from "../../../Core/Badge/Badge";
import * as AdhConfig from "../../../Core/Config/Config";
import * as AdhCredentials from "../../../Core/User/Credentials";
import * as AdhHttp from "../../../Core/Http/Http";
import * as AdhPermissions from "../../../Core/Permissions/Permissions";
import * as AdhPreliminaryNames from "../../../Core/PreliminaryNames/PreliminaryNames";
import * as AdhTopLevelState from "../../../Core/TopLevelState/TopLevelState";

import * as AdhMercator2015Proposal from "../../2015/Proposal/Proposal";

import * as ResourcesBase from "../../../../ResourcesBase";

import * as SIBadgeable from "../../../../Resources_/adhocracy_core/sheets/badge/IBadgeable";
import * as SIBadgeAssignment from "../../../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment";
import * as SIChallenge from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IChallenge";
import * as SICommentable from "../../../../Resources_/adhocracy_core/sheets/comment/ICommentable";
import * as SICommunity from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ICommunity";
import * as SIConnectionCohesion from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IConnectionCohesion";
import * as SIDescription from "../../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SIDifference from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IDifference";
import * as SIDuration from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IDuration";
import * as SIExtraFunding from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IExtraFunding";
import * as SIExtraInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IExtraInfo";
import * as SIFinancialPlanning from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IFinancialPlanning";
import * as SIGoal from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IGoal";
import * as SIImageReference from "../../../../Resources_/adhocracy_core/sheets/image/IImageReference";
import * as SILocation from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ILocation";
import * as SILogbook from "../../../../Resources_/adhocracy_core/sheets/logbook/IHasLogbookPool";
import * as SIMercatorIntroImageMetadata from "../../../../Resources_/adhocracy_mercator/sheets/mercator/IIntroImageMetadata";
import * as SIMercatorSubResources from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IMercatorSubResources";
import * as SIMercatorUserInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IUserInfo";
import * as SIMetaData from "../../../../Resources_/adhocracy_core/sheets/metadata/IMetadata";
import * as SIOrganizationInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IOrganizationInfo";
import * as SIPartners from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IPartners";
import * as SIPitch from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IPitch";
import * as SIPlan from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IPlan";
import * as SIPracticalRelevance from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IPracticalRelevance";
import * as SIStatus from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IStatus";
import * as SITarget from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ITarget";
import * as SITeam from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ITeam";
import * as SITitle from "../../../../Resources_/adhocracy_core/sheets/title/ITitle";
import * as SITopic from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ITopic";
import * as SIUserInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IUserInfo";
import * as SIWinnerInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IWinnerInfo";
import RIBadgeAssignment from "../../../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment";
import RIChallenge from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IChallenge";
import RIConnectionCohesion from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IConnectionCohesion";
import RIDifference from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IDifference";
import RIDuration from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IDuration";
import RIExtraInfo from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IExtraInfo";
import RIGoal from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IGoal";
import RIMercatorIntroImage from "../../../../Resources_/adhocracy_mercator/resources/mercator/IIntroImage";
import RIMercatorProposal from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IMercatorProposal";
import RIPartners from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPartners";
import RIPitch from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPitch";
import RIPlan from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPlan";
import RIPracticalRelevance from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPracticalRelevance";
import RITarget from "../../../../Resources_/adhocracy_mercator/resources/mercator2/ITarget";
import RITeam from "../../../../Resources_/adhocracy_mercator/resources/mercator2/ITeam";

var pkgLocation = "/Mercator/2016/Proposal";

var topics = [
    "democracy_and_participation",
    "arts_and_cultural_activities",
    "environment",
    "social_inclusion",
    "migration",
    "communities",
    "urban_development",
    "education",
    "other",
];

var topicTrString = (topic : string) : string => {
    var topicTranslations = {
        democracy_and_participation: "TR__MERCATOR_TOPIC_DEMOCRACY",
        arts_and_cultural_activities: "TR__MERCATOR_TOPIC_CULTURE",
        environment: "TR__MERCATOR_TOPIC_ENVIRONMENT",
        social_inclusion: "TR__MERCATOR_TOPIC_SOCIAL",
        migration: "TR__MERCATOR_TOPIC_MIGRATION",
        communities: "TR__MERCATOR_TOPIC_COMMUNITY",
        urban_development: "TR__MERCATOR_TOPIC_URBAN",
        education: "TR__MERCATOR_TOPIC_EDUCATION",
        other: "TR__MERCATOR_TOPIC_OTHER"
    };
    return topicTranslations[topic];
};


export interface IData {
    logbookPoolPath : string;
    userInfo : {
        firstName : string;
        lastName : string;
    };
    organizationInfo : {
        name : string;
        website : string;
        city : string;
        country : string;
        status : string;
        otherText : string;
        registrationDate : string;
        helpRequest : string;
    };
    title : string;
    introduction : {
        pitch : string;
        picture : string;
    };
    partners : {
        hasPartners : boolean;
        partner1 : {
            name : string;
            country : string;
            website : string;
        };
        partner2 : {
            name : string;
            country : string;
            website : string;
        };
        partner3 : {
            name : string;
            country : string;
            website : string;
        };
        hasOther : boolean;
        otherText : string;
    };
    topic : {
        democracy_and_participation : boolean;
        arts_and_cultural_activities : boolean;
        environment : boolean;
        social_inclusion : boolean;
        migration : boolean;
        communities : boolean;
        urban_development : boolean;
        education : boolean;
        other : boolean;
        otherText : string;
    };
    duration : number;
    location : {
        location_is_linked_to_ruhr : boolean;
        location_is_linked_to_ruhr_text : string;
        location_is_online : boolean;
        location_is_specific : boolean;
        location_specific : string;
    };
    status : string;
    impact : {
        challenge : string;
        goal : string;
        plan : string;
        target : string;
        team : string;
        extraInfo : string;
    };
    criteria : {
        strengthen : string;
        difference : string;
        practical : string;
    };
    finance : {
        budget : number;
        requestedFunding : number;
        major : string;
        otherSources? : string;
        secured? : boolean;
    };
    experience : string;
    heardFrom? : {
        facebook : boolean;
        newsletter : boolean;
        other : boolean;
        otherText : string;
        personal_contact : boolean;
        twitter : boolean;
        website : boolean;
    };
    winner : {
        funding : number;
        description : string;
        name : string;
    };
}

export interface IDetailData extends IData {
    commentCountTotal : number;
    commentCounts: {
        proposal : number;
        pitch : number;
        partners : number;
        duration : number;
        challenge : number;
        goal : number;
        plan : number;
        target : number;
        team : number;
        extrainfo : number;
        connectioncohesion : number;
        difference : number;
        practicalrelevance : number;
    };
    supporterCount : number;
    creationDate : string;
    creator : string;
    selectedTopics : string[];
}

export interface IFormData extends IData {
    acceptDisclaimer : boolean;
}


var fill = (data : IFormData, resource) => {
    switch (resource.content_type) {
        case RIMercatorProposal.content_type:
            SIUserInfo.set(resource, {
                first_name: data.userInfo.firstName,
                last_name: data.userInfo.lastName
            });
            SIOrganizationInfo.set(resource, {
                name: data.organizationInfo.name,
                city: data.organizationInfo.city,
                country: data.organizationInfo.country,
                help_request: data.organizationInfo.helpRequest,
                registration_date: data.organizationInfo.registrationDate,
                website: data.organizationInfo.website,
                status: data.organizationInfo.status,
                status_other: data.organizationInfo.otherText
            });
            SITopic.set(resource, {
                topic: _.reduce(<any>data.topic, (result, include, topic) => {
                    if (include && (topic !== "otherText")) {
                        result.push(topic);
                    }
                    return result;
                }, []),
                topic_other: data.topic.otherText
            });
            SITitle.set(resource, {
                title: data.title
            });
            SILocation.set(resource, {
                location: data.location.location_specific,
                is_online: !!data.location.location_is_online,
                has_link_to_ruhr: !!data.location.location_is_linked_to_ruhr,
                link_to_ruhr: data.location.location_is_linked_to_ruhr_text
            });
            SIStatus.set(resource, {
                status: data.status
            });
            SIFinancialPlanning.set(resource, {
                budget: data.finance.budget,
                requested_funding: data.finance.requestedFunding,
                major_expenses: data.finance.major
            });
            SIExtraFunding.set(resource, {
                other_sources: data.finance.otherSources,
                secured: !!data.finance.secured
            });
            SICommunity.set(resource, {
                expected_feedback: data.experience,
                heard_froms: _.reduce(<any>data.heardFrom, (result, include, item) => {
                    if (include && item !== "otherText" ) {
                        result.push(item);
                    }
                    return result;
                }, []),
                heard_from_other: data.heardFrom.otherText
            });
            SIImageReference.set(resource, {
                picture: data.introduction.picture
            });
            break;
        case RIPitch.content_type:
            SIPitch.set(resource, {
                pitch: data.introduction.pitch
            });
            break;
        case RIPartners.content_type:
            SIPartners.set(resource, {
                has_partners: (<any>data.partners.hasPartners === "true" ? true : false),
                partner1_name: data.partners.partner1.name,
                partner1_website: data.partners.partner1.website,
                partner1_country: data.partners.partner1.country,
                partner2_name: data.partners.partner2.name,
                partner2_website: data.partners.partner2.website,
                partner2_country: data.partners.partner2.country,
                partner3_name: data.partners.partner3.name,
                partner3_website: data.partners.partner3.website,
                partner3_country: data.partners.partner3.country,
                other_partners: data.partners.otherText
            });
            break;
        case RIDuration.content_type:
            SIDuration.set(resource, {
                duration: data.duration
            });
            break;
        case RIChallenge.content_type:
            SIChallenge.set(resource, {
                challenge: data.impact.challenge
            });
            break;
        case RIGoal.content_type:
            SIGoal.set(resource, {
                goal: data.impact.goal
            });
            break;
        case RIPlan.content_type:
            SIPlan.set(resource, {
                plan: data.impact.plan
            });
            break;
        case RITarget.content_type:
            SITarget.set(resource, {
                target: data.impact.target
            });
            break;
        case RITeam.content_type:
            SITeam.set(resource, {
                team: data.impact.team
            });
            break;
        case RIExtraInfo.content_type:
            SIExtraInfo.set(resource, {
                extrainfo: data.impact.extraInfo
            });
            break;
        case RIConnectionCohesion.content_type:
            SIConnectionCohesion.set(resource, {
                connection_cohesion: data.criteria.strengthen
            });
            break;
        case RIDifference.content_type:
            SIDifference.set(resource, {
                difference: data.criteria.difference
            });
            break;
        case RIPracticalRelevance.content_type:
            SIPracticalRelevance.set(resource, {
                practicalrelevance: data.criteria.practical
            });
            break;
    }
};

var create = (
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (scope) => {
    var data : IFormData = scope.data;
    return adhHttp.withTransaction((transaction) => {
        var proposal : ResourcesBase.IResource = {
            path: adhPreliminaryNames.nextPreliminary(),
            content_type: RIMercatorProposal.content_type,
            data: {},
        };
        fill(data, proposal);
        var proposalRequest = transaction.post(scope.poolPath, proposal);

        var subResourcesSheet = <any>{};
        _.forEach({
            pitch: RIPitch,
            partners: RIPartners,
            duration: RIDuration,
            challenge: RIChallenge,
            goal: RIGoal,
            plan: RIPlan,
            target: RITarget,
            team: RITeam,
            extrainfo: RIExtraInfo,
            connectioncohesion: RIConnectionCohesion,
            difference: RIDifference,
            practicalrelevance: RIPracticalRelevance
        }, (cls, subresourceKey : string) => {
            var resource = new cls({preliminaryNames: adhPreliminaryNames});
            fill(data, resource);
            var request = transaction.post(proposalRequest.path, resource);
            subResourcesSheet[subresourceKey] = request.path;
        });

        var proposal2 : ResourcesBase.IResource = {
            path: adhPreliminaryNames.nextPreliminary(),
            content_type: RIMercatorProposal.content_type,
            data: {},
        };
        SIMercatorSubResources.set(proposal2, subResourcesSheet);
        transaction.put(proposalRequest.path, proposal2);

        return transaction.commit().then((responses) => {
            return responses[0].path;
        });
    });
};

var edit = (
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (scope) => {
    var data : IFormData = scope.data;
    return adhHttp.get(scope.path).then((oldProposal) => {
        var subResourcesSheet = SIMercatorSubResources.get(oldProposal);

        return adhHttp.withTransaction((transaction) => {
            var proposal : ResourcesBase.IResource = {
                path: adhPreliminaryNames.nextPreliminary(),
                content_type: RIMercatorProposal.content_type,
                data: {},
            };
            fill(data, proposal);
            // ICommunity can and should not be changed on edit
            delete SICommunity.get(proposal);
            transaction.put(oldProposal.path, proposal);

            _.forEach({
                pitch: RIPitch,
                partners: RIPartners,
                duration: RIDuration,
                challenge: RIChallenge,
                goal: RIGoal,
                plan: RIPlan,
                target: RITarget,
                team: RITeam,
                extrainfo: RIExtraInfo,
                connectioncohesion: RIConnectionCohesion,
                difference: RIDifference,
                practicalrelevance: RIPracticalRelevance
            }, (cls, subresourceKey : string) => {
                var resource = new cls({preliminaryNames: adhPreliminaryNames});
                fill(data, resource);
                transaction.put(subResourcesSheet[subresourceKey], resource);
            });

            return transaction.commit();
        });
    });
};

var moderate = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhCredentials : AdhCredentials.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => (scope) => {
    var badges = {
        winning: adhTopLevelState.get("processUrl") + "badges/winning/",
        community: adhTopLevelState.get("processUrl") + "badges/community/",
        shortlist: adhTopLevelState.get("processUrl") + "badges/shortlist/",
    };

    return adhHttp.get(scope.path).then((oldProposal) => {
        var clone = {
            content_type: oldProposal.content_type,
            data: {}
        };
        SIWinnerInfo.set(clone, {
            funding: scope.data.winner.funding
        });
        var resourcePromise = adhHttp.put(scope.path, clone);

        var badgePoolPath = SIBadgeable.get(oldProposal).post_pool;
        var assignmentRequests = _.map(SIBadgeable.get(oldProposal).assignments, (p : string) => adhHttp.get(p));
        var badgePromise = $q.all(assignmentRequests).then((assignments) => {
            var communityAssignment = <any>_.find(assignments, (a : any) => {
                return SIBadgeAssignment.get(a).badge === badges.community;
            });
            var winningAssignment = <any>_.find(assignments, (a : any) => {
                return SIBadgeAssignment.get(a).badge === badges.winning;
            });
            var badgeAssignment = communityAssignment || winningAssignment;

            var postdata : any;
            if (badgeAssignment) {
                postdata = {
                    content_type: RIBadgeAssignment.content_type,
                    data: {}
                };
                SIDescription.set(postdata, {
                    description: scope.data.winner.description
                });
                return adhHttp.put(badgeAssignment.path, postdata);
            } else {
                postdata = {
                    content_type: RIBadgeAssignment.content_type,
                    data: {}
                };
                SIDescription.set(postdata, {
                    description: scope.data.winner.description
                });
                SIBadgeAssignment.set(postdata, {
                    badge: badges[scope.data.winner.name],
                    object: scope.path,
                    subject: adhCredentials.userPath
                });
                return adhHttp.post(badgePoolPath, postdata);
            }
        });

        return $q.all([resourcePromise, badgePromise]);
    });
};

var get = (
    $q : ng.IQService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadgeAssignments
) => (path : string) : ng.IPromise<IDetailData> => {
    return adhHttp.get(path).then((proposal) => {
        var subs : {
            pitch : ResourcesBase.IResource
            partners : ResourcesBase.IResource
            duration : ResourcesBase.IResource
            challenge : ResourcesBase.IResource
            goal : ResourcesBase.IResource
            plan : ResourcesBase.IResource
            target : ResourcesBase.IResource
            team : ResourcesBase.IResource
            extrainfo : ResourcesBase.IResource
            connectioncohesion : ResourcesBase.IResource
            difference : ResourcesBase.IResource
            practicalrelevance : ResourcesBase.IResource
        } = <any>{};

        return $q.all(_.map(<any>SIMercatorSubResources.get(proposal), (path, key) => {
            return adhHttp.get(<string>path).then((subresource) => {
                subs[key] = subresource;
            });
        })).then(() => $q.all([
            AdhMercator2015Proposal.countSupporters(adhHttp, path + "rates/", path),
            adhGetBadges(proposal).then((assignments : AdhBadge.IBadge[]) => {
                var communityAssignment = _.find(assignments, (a) => a.name === "community");
                var winningAssignment = _.find(assignments, (a) => a.name === "winning");
                var shortlistAssignment = _.find(assignments, (a) => a.name === "shortlist");

                return communityAssignment || winningAssignment || shortlistAssignment;
            })
        ])).then((args : any[]) : IDetailData => {
            var commentCounts = {
                proposal: SICommentable.get(proposal).comments_count,
                pitch: SICommentable.get(subs.pitch).comments_count,
                partners: SICommentable.get(subs.partners).comments_count,
                duration: SICommentable.get(subs.duration).comments_count,
                challenge: SICommentable.get(subs.challenge).comments_count,
                goal: SICommentable.get(subs.goal).comments_count,
                plan: SICommentable.get(subs.plan).comments_count,
                target: SICommentable.get(subs.target).comments_count,
                team: SICommentable.get(subs.team).comments_count,
                extrainfo: SICommentable.get(subs.extrainfo).comments_count,
                connectioncohesion: SICommentable.get(subs.connectioncohesion).comments_count,
                difference: SICommentable.get(subs.difference).comments_count,
                practicalrelevance: SICommentable.get(subs.practicalrelevance).comments_count
            };

            return {
                supporterCount: args[0],

                creationDate: SIMetaData.get(proposal).item_creation_date,
                creator: SIMetaData.get(proposal).creator,
                logbookPoolPath: SILogbook.get(proposal).logbook_pool,

                userInfo: {
                    firstName: SIMercatorUserInfo.get(proposal).first_name,
                    lastName: SIMercatorUserInfo.get(proposal).last_name
                },
                organizationInfo: {
                    name: SIOrganizationInfo.get(proposal).name,
                    city: SIOrganizationInfo.get(proposal).city,
                    country: SIOrganizationInfo.get(proposal).country,
                    helpRequest: SIOrganizationInfo.get(proposal).help_request,
                    registrationDate: SIOrganizationInfo.get(proposal).registration_date,
                    website: SIOrganizationInfo.get(proposal).website,
                    status: SIOrganizationInfo.get(proposal).status,
                    otherText: SIOrganizationInfo.get(proposal).status_other
                },
                topic: <any>_.reduce(<any>topics, (result, key : string) => {
                    result[key] = _.indexOf(SITopic.get(proposal).topic, key) !== -1;
                    return result;
                }, {
                    otherText: SITopic.get(proposal).topic_other
                }),
                selectedTopics: _.map(SITopic.get(proposal).topic, (topic : string) => {
                    if (topic === "other") {
                        return SITopic.get(proposal).topic_other;
                    } else {
                        return topicTrString(topic);
                    }
                }),
                title: SITitle.get(proposal).title,
                location: {
                    location_is_specific: !!SILocation.get(proposal).location,
                    location_specific: SILocation.get(proposal).location,
                    location_is_online: SILocation.get(proposal).is_online,
                    location_is_linked_to_ruhr: SILocation.get(proposal).has_link_to_ruhr,
                    location_is_linked_to_ruhr_text: SILocation.get(proposal).link_to_ruhr
                },
                status: SIStatus.get(proposal).status,
                finance: {
                    budget: SIFinancialPlanning.get(proposal).budget,
                    requestedFunding: SIFinancialPlanning.get(proposal).requested_funding,
                    major: SIFinancialPlanning.get(proposal).major_expenses,
                    otherSources: (SIExtraFunding.get(proposal) || {}).other_sources,
                    secured: (SIExtraFunding.get(proposal) || {}).secured
                },
                experience: SICommunity.get(proposal).expected_feedback,
                heardFrom: _.reduce(SICommunity.get(proposal).heard_froms, (result, item : string) => {
                    result[item] = true;
                    return result;
                }, {}),
                winner: {
                    funding: (SIWinnerInfo.get(proposal) || {}).funding,
                    description: (args[1] || {}).description,
                    name: (args[1] || {}).name
                },
                introduction: {
                    pitch: SIPitch.get(subs.pitch).pitch,
                    picture: SIImageReference.get(proposal).picture
                },
                partners: {
                    hasPartners: SIPartners.get(subs.partners).has_partners,
                    partner1: {
                        name: SIPartners.get(subs.partners).partner1_name,
                        website: SIPartners.get(subs.partners).partner1_website,
                        country: SIPartners.get(subs.partners).partner1_country
                    },
                    partner2: {
                        name: SIPartners.get(subs.partners).partner2_name,
                        website: SIPartners.get(subs.partners).partner2_website,
                        country: SIPartners.get(subs.partners).partner2_country
                    },
                    partner3: {
                        name: SIPartners.get(subs.partners).partner3_name,
                        website: SIPartners.get(subs.partners).partner3_website,
                        country: SIPartners.get(subs.partners).partner3_country
                    },
                    hasOther: !!SIPartners.get(subs.partners).other_partners,
                    otherText: SIPartners.get(subs.partners).other_partners
                },
                duration: SIDuration.get(subs.duration).duration,
                impact: {
                    challenge: SIChallenge.get(subs.challenge).challenge,
                    goal: SIGoal.get(subs.goal).goal,
                    plan: SIPlan.get(subs.plan).plan,
                    target: SITarget.get(subs.target).target,
                    team: SITeam.get(subs.team).team,
                    extraInfo: SIExtraInfo.get(subs.extrainfo).extrainfo
                },
                criteria: {
                    strengthen: SIConnectionCohesion.get(subs.connectioncohesion).connection_cohesion,
                    difference: SIDifference.get(subs.difference).difference,
                    practical: SIPracticalRelevance.get(subs.practicalrelevance).practicalrelevance
                },
                commentCounts: commentCounts,
                commentCountTotal: _.sum(_.values(commentCounts))
            };
        });
    });
};


export var createDirective = (
    $location : angular.ILocationService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrl
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            poolPath: "@"
        },
        link: (scope) => {
            scope.create = true;

            scope.data = {
                user_info: {},
                organization_info: {},
                introduction: {},
                partners: {
                    partner1: {},
                    partner2: {},
                    partner3: {}
                },
                topic: {},
                location: {},
                impact: {},
                criteria: {},
                finance: {},
                heardFrom: {},
                winner: {}
            };

            scope.submit = () => create(adhHttp, adhPreliminaryNames)(scope).then((proposalPath) => {
                $location.url(adhResourceUrl(proposalPath));
            });

            scope.cancel = () => {
                adhTopLevelState.goToCameFrom(adhResourceUrl(adhTopLevelState.get("processUrl")));
            };
        }
    };
};

export var editDirective = (
    $q : angular.IQService,
    $location : angular.ILocationService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhResourceUrl,
    adhGetBadges : AdhBadge.IGetBadgeAssignments
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.data = {
                user_info: {},
                organization_info: {},
                introduction: {},
                partners: {
                    partner1: {},
                    partner2: {},
                    partner3: {}
                },
                topic: {},
                location: {},
                impact: {},
                criteria: {},
                finance: {},
                heardFrom: {},
                winner: {}
            };

            get($q, adhHttp, adhTopLevelState, adhGetBadges)(scope.path).then((data) => {
                scope.data = data;

                scope.data.partners.hasPartners = scope.data.partners.hasPartners ? "true" : "false";

                if (scope.data.organizationInfo.status === "planned_nonprofit") {
                    scope.data.organizationInfo.registrationDateField = data.organizationInfo.registrationDate.substr(0, 7);
                } else if (scope.data.organizationInfo.status === "registered_nonprofit") {
                    scope.data.organizationInfo.registrationDateField = data.organizationInfo.registrationDate.substr(0, 4);
                }
            });

            scope.submit = () => edit(adhHttp, adhPreliminaryNames)(scope).then(() => {
                $location.url(adhResourceUrl(scope.path));
            });

            scope.cancel = () => {
                adhTopLevelState.goToCameFrom(adhResourceUrl(scope.path));
            };
        }
    };
};

export var moderateDirective = (
    $q : angular.IQService,
    $location : angular.ILocationService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhResourceUrl,
    adhGetBadges : AdhBadge.IGetBadgeAssignments,
    adhCredentials : AdhCredentials.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Moderate.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.data = {
                user_info: {},
                organization_info: {},
                introduction: {},
                partners: {
                    partner1: {},
                    partner2: {},
                    partner3: {}
                },
                topic: {},
                location: {},
                impact: {},
                criteria: {},
                finance: {},
                heardFrom: {},
                winner: {}
            };

            get($q, adhHttp, adhTopLevelState, adhGetBadges)(scope.path).then((data) => {
                scope.data = data;
                scope.create = !data.winner.name;
            });

            scope.submit = () => moderate($q, adhHttp, adhPreliminaryNames, adhCredentials, adhTopLevelState)(scope).then(() => {
                $location.url(adhResourceUrl(scope.path));
            });

            scope.cancel = () => {
                adhTopLevelState.goToCameFrom(adhResourceUrl(scope.path));
            };
        }
    };
};

export var listing = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            path: "@",
            update: "=?",
            facets: "=?",
            sort: "=?",
            sorts: "=?",
            initialLimit: "=?",
            params: "=?"
        },
        link: (scope) => {
            scope.contentType = RIMercatorProposal.content_type;
        }
    };
};

export var listItem = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges : AdhBadge.IGetBadgeAssignments
) => {
    return {
        retrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/../../2015/Proposal/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope, element) => {
            scope.$on("$destroy", adhTopLevelState.bind("processState", scope));
            get($q, adhHttp, adhTopLevelState, adhGetBadges)(scope.path).then((data) => {

                scope.data = {
                    title: {
                        title: data.title
                    },
                    user_info: {
                        first_name: data.userInfo.firstName,
                        last_name: data.userInfo.lastName,
                        createtime: data.creationDate,
                        path: data.creator
                    },
                    organization_info: data.organizationInfo,
                    finance: {
                        requested_funding: data.finance.requestedFunding
                    },
                    introduction: data.introduction,
                    commentCountTotal: data.commentCountTotal,
                    supporterCount: data.supporterCount,
                    winnerBadgeAssignment: data.winner.name ? data.winner : null
                };

                scope.$on("$destroy", adhTopLevelState.bind("processState", scope.data, "currentPhase"));

                scope.$on("$destroy", adhTopLevelState.on("proposalUrl", (proposalVersionUrl) => {
                    if (!proposalVersionUrl) {
                        scope.selectedState = "";
                    } else if (proposalVersionUrl === scope.path) {
                        scope.selectedState = "is-selected";
                    } else {
                        scope.selectedState = "is-not-selected";
                    }
                }));
            });
        }
    };
};

export var mercatorProposalFormController2016 = (
    $scope,
    $element,
    adhShowError,
    adhTopLevelState : AdhTopLevelState.Service,
    adhSubmitIfValid,
    adhResourceUrl,
    adhUploadImage,
    flowFactory,
    $translate
) => {
    $translate.use("en");

    $scope.$flow = flowFactory.create();

    // Fixme: These links are not used currently due to them not working on production/staging
    // See https://github.com/liqd/adhocracy3/issues/2011
    $scope.selection_criteria_link = "http://advocate-europe.eu/en/idea-space/selection-criteria/";
    $scope.financial_plan_link = "http://advocate-europe.eu/de/media/advocate-europe_project-financial-plan.xlsx";

    var topicTotal = () => {
        return _.reduce($scope.data.topic, (result, include, topic : string) => {
            if (include && (topic !== "otherText")) {
                return result + 1;
            } else {
                return result;
            }
        }, 0);
    };

    $scope.topics = topics;

    var heardFromCheckboxes = [
        "heard-from-personal",
        "heard-from-website",
        "heard-from-newsletter",
        "heard-from-facebook",
        "heard-from-twitter",
        "heard-from-other"
    ];

    var locationCheckboxes = [
        "location-location-is-specific",
        "location-location-is-online",
        "location-location-is-linked-to-ruhr"
    ];

    $scope.topicChange = (isChecked) => {
        if ($scope.data.topic) {
            var validity = topicTotal() > 0 && topicTotal() < 3;
            $scope.mercatorProposalForm.mercatorProposalBriefForm["introduction-topics"].$setValidity("enoughTopics", validity);
            $scope.mercatorProposalForm.mercatorProposalBriefForm["introduction-topics"].$setDirty();
        } else {
            $scope.mercatorProposalForm.mercatorProposalBriefForm["introduction-topics"].$setValidity("enoughTopics", false);
            $scope.mercatorProposalForm.mercatorProposalBriefForm["introduction-topics"].$setDirty();
        }
    };

    var updateCheckBoxGroupValidity = (form, names : string[]) : boolean => {
        var valid =  _.some(names, (name) => form[name].$modelValue);
        _.forOwn(names, (name) => {
            form[name].$setValidity("groupRequired", valid);
        });
        return valid;
    };

    $scope.topicTrString = topicTrString;

    var showCheckboxGroupError = (form, names : string[]) : boolean => {
        var dirty = $scope.mercatorProposalForm.$submitted || _.some(names, (name) => form[name].$dirty);
        return !updateCheckBoxGroupValidity(form, names) && dirty;
    };

    $scope.showTopicsError = () : boolean => {
        return ((topicTotal() < 1) || (topicTotal() > 2)) &&
            ($scope.mercatorProposalForm.mercatorProposalBriefForm["introduction-topics"].$dirty ||
                $scope.mercatorProposalForm.$submitted);
    };

    $scope.showLocationError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalBriefForm, locationCheckboxes);
    };

    $scope.showStatusError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalBriefForm, locationCheckboxes);
    };

    $scope.showFinanceGrantedInfo = () : boolean => {
        return ($scope.data.finance && $scope.data.finance.otherSources && $scope.data.finance.otherSources !== "");
    };

    $scope.showHeardFromError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalCommunityForm, heardFromCheckboxes);
    };

    $scope.dateChange = (date) => {
        // FIXME: this is quite hacky dates need proper validation EG not so much in the past or future too
        if ($scope.data.organizationInfo.status === "planned_nonprofit") {
            $scope.data.organizationInfo.registrationDate = $scope.data.organizationInfo.registrationDateField + "-01";
        } else {
            $scope.data.organizationInfo.registrationDate = $scope.data.organizationInfo.registrationDateField + "-01-01";
        }
    };

    $scope.showError = adhShowError;

    $scope.submitIfValid = () => {
        adhSubmitIfValid($scope, $element, $scope.mercatorProposalForm, () => {
            if ($scope.$flow && $scope.$flow.support && $scope.$flow.files.length > 0) {
                return adhUploadImage(
                    adhTopLevelState.get("processUrl"),
                    $scope.$flow,
                    RIMercatorIntroImage.content_type,
                    SIMercatorIntroImageMetadata.nick
                ).then((imageUrl : string) => {
                    $scope.data.introduction.picture = imageUrl;
                    return $scope.submit();
                });
            } else {
                return $scope.submit();
            }
        });
    };
};

export var detailDirective = (
    $q : ng.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhPermissions : AdhPermissions.Service,
    adhGetBadges : AdhBadge.IGetBadgeAssignments,
    $translate
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            $translate.use("en");
            adhPermissions.bindScope(scope, () => scope.path);
            // FIXME, waa
            scope.isModerator = scope.options.PUT;
            scope.$on("$destroy", adhTopLevelState.bind("processState", scope));
            get($q, adhHttp, adhTopLevelState, adhGetBadges)(scope.path).then((data) => {
                scope.data = data;
            });

            scope.$on("$destroy", adhTopLevelState.bind("processState", scope));
            scope.$on("$destroy", adhTopLevelState.bind("view", scope, "proposalTab"));

            scope.showBlogTabs = () => {
                return scope.data && scope.data.winner.name && scope.processState === "result";
            };
        }
    };
};
