/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import * as AdhConfig from "../../../Config/Config";
import * as AdhPreliminaryNames from "../../../PreliminaryNames/PreliminaryNames";

import * as SIChallenge from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IChallenge";
import * as SICommunity from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ICommunity";
import * as SIDifference from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IDifference";
import * as SIDuration from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IDuration";
import * as SIExtraFunding from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IExtraFunding";
import * as SIExtraInfo from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IExtraInfo";
import * as SIFinancialPlanning from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IFinancialPlanning";
import * as SIGoal from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IGoal";
import * as SILocation from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/ILocation";
import * as SIMercatorSubResources from "../../../../Resources_/adhocracy_mercator/sheets/mercator2/IMercatorSubResources";
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
import RIChallenge from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IChallenge";
import RIConnectionCohesion from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IConnectionCohesion";
import RIDifference from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IDifference";
import RIDuration from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IDuration";
import RIExtraInfo from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IExtraInfo";
import RIGoal from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IGoal";
import RIMercatorProposal from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IMercatorProposal";
import RIPartners from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPartners";
import RIPitch from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPitch";
import RIPlan from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPlan";
import RIPracticalRelevance from "../../../../Resources_/adhocracy_mercator/resources/mercator2/IPracticalRelevance";
import RITarget from "../../../../Resources_/adhocracy_mercator/resources/mercator2/ITarget";
import RITeam from "../../../../Resources_/adhocracy_mercator/resources/mercator2/ITeam";

var pkgLocation = "/Mercator/2016/Proposal";


export interface IData {
    userInfo : {
        firstName : string;
        lastName : string;
    };
    organizationInfo : {
        name : string;
        email : string;
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
        imageUpload : any;
        picture : any;
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
        democracy : boolean;
        culture : boolean;
        environment : boolean;
        social : boolean;
        migration : boolean;
        community : boolean;
        urban : boolean;
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
        location_specific_1 : string;
        location_specific_2 : string;
        location_specific_3 : string;
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
        otherSources : string;
        secured : boolean;
        experience : string;
    };
    heardFrom : {
        facebook : boolean;
        newsletter : boolean;
        other : boolean;
        otherText : string;
        personal_contact : boolean;
        twitter : boolean;
        website : boolean;
    };
    acceptDisclaimer : boolean;
}


var fill = (data : IData, resource) => {
    switch (resource.content_type) {
        case RIMercatorProposal.content_type:
            resource.data[SIMercatorSubResources.nick] = new SIMercatorSubResources.Sheet(<any>{});
            resource.data[SIUserInfo.nick] = new SIUserInfo.Sheet({
                first_name: data.userInfo.firstName,
                last_name: data.userInfo.lastName
            });
            resource.data[SIOrganizationInfo.nick] = new SIOrganizationInfo.Sheet({
                name: data.organizationInfo.name,
                city: data.organizationInfo.city,
                country: data.organizationInfo.country,
                help_request: data.organizationInfo.helpRequest,
                registration_date: data.organizationInfo.registrationDate,
                website: data.organizationInfo.website,
                contact_email: data.organizationInfo.email,
                status: data.organizationInfo.status,
                status_other: data.organizationInfo.otherText
            });
            resource.data[SITopic.nick] = new SITopic.Sheet({
                topic: null,  // FIXME
                other: data.topic.otherText
            });
            resource.data[SITitle.nick] = new SITitle.Sheet({
                title: data.title
            });
            resource.data[SILocation.nick] = new SILocation.Sheet({
                location: null,  // FIXME
                is_online: data.location.location_is_online,
                has_link_to_ruhr: data.location.location_is_linked_to_ruhr,
                link_to_ruhr: data.location.location_is_linked_to_ruhr_text
            });
            resource.data[SIStatus.nick] = new SIStatus.Sheet({
                status: data.status
            });
            resource.data[SIFinancialPlanning.nick] = new SIFinancialPlanning.Sheet({
                budget: data.finance.budget,
                requested_funding: data.finance.requestedFunding,
                major_expenses: data.finance.major
            });
            resource.data[SIExtraFunding.nick] = new SIExtraFunding.Sheet({
                other_sources: data.finance.otherSources,
                secured: data.finance.secured
            });
            resource.data[SICommunity.nick] = new SICommunity.Sheet({
                expected_feedback: null,  // FIXME
                heard_from: null,  // FIXME
                heard_from_other: data.heardFrom.otherText
            });
            resource.data[SIWinnerInfo.nick] = new SIWinnerInfo.Sheet({
                explanation: null,  // FIXME
                funding: null  // FIXME
            });
            break;
        case RIPitch.content_type:
            resource.data[SIPitch.nick] = new SIPitch.Sheet({
                pitch: data.introduction.pitch
            });
            break;
        case RIPartners.content_type:
            resource.data[SIPartners.nick] = new SIPartners.Sheet({
                has_partners: data.partners.hasPartners,
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
            resource.data[SIDuration.nick] = new SIDuration.Sheet({
                duration: data.duration
            });
            break;
        case RIChallenge.content_type:
            resource.data[SIChallenge.nick] = new SIChallenge.Sheet({
                challenge: data.impact.challenge
            });
            break;
        case RIGoal.content_type:
            resource.data[SIGoal.nick] = new SIGoal.Sheet({
                goal: data.impact.goal
            });
            break;
        case RIPlan.content_type:
            resource.data[SIPlan.nick] = new SIPlan.Sheet({
                plan: data.impact.plan
            });
            break;
        case RITarget.content_type:
            resource.data[SITarget.nick] = new SITarget.Sheet({
                target: data.impact.target
            });
            break;
        case RITeam.content_type:
            resource.data[SITeam.nick] = new SITeam.Sheet({
                team: data.impact.team
            });
            break;
        case RIExtraInfo.content_type:
            resource.data[SIExtraInfo.nick] = new SIExtraInfo.Sheet({
                extrainfo: data.impact.extraInfo
            });
            break;
        case RIDifference.content_type:
            resource.data[SIDifference.nick] = new SIDifference.Sheet({
                difference: data.criteria.difference
            });
            break;
        case RIPracticalRelevance.content_type:
            resource.data[SIPracticalRelevance.nick] = new SIPracticalRelevance.Sheet({
                practicalrelevance: data.criteria.practical
            });
            break;
    }
};

var create = (scope, adhPreliminaryNames) => {
    var data : IData = scope.data;
    var proposal = new RIMercatorProposal({preliminaryNames: adhPreliminaryNames});
    proposal.parent = scope.poolPath;
    fill(data, proposal);

    var subresources = _.map({
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
        resource.parent = proposal.path;
        fill(data, resource);
        proposal.data[SIMercatorSubResources.nick][subresourceKey] = resource.path;
        return resource;
    });

    return _.flatten([proposal, subresources]);
};


export var createDirective = (
    adhConfig : AdhConfig.IService,
    flowFactory
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {},
        link: (scope) => {
            scope.$flow = flowFactory.create();
        }
    };
};

export var mercatorProposalFormController2016 = (
    $scope,
    $element,
    $window,
    adhShowError,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => {

    $scope.data = {
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
        heardFrom: {}
    };

    var topicTotal = 0;

    $scope.topics = [
        "democracy",
        "culture",
        "environment",
        "social",
        "migration",
        "community",
        "urban",
        "education",
        "other",
    ];

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
            topicTotal = isChecked ? (topicTotal + 1) : (topicTotal - 1);
            var validity = topicTotal > 0 && topicTotal < 3;
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

    $scope.topicTrString = (topic) => {
        var topics = {
            democracy: "TR__MERCATOR_TOPIC_DEMOCRACY",
            culture: "TR__MERCATOR_TOPIC_CULTURE",
            environment: "TR__MERCATOR_TOPIC_ENVIRONMENT",
            social: "TR__MERCATOR_TOPIC_SOCIAL",
            migration: "TR__MERCATOR_TOPIC_MIGRATION",
            community: "TR__MERCATOR_TOPIC_COMMUNITY",
            urban: "TR__MERCATOR_TOPIC_URBAN",
            education: "TR__MERCATOR_TOPIC_EDUCATION",
            other: "TR__MERCATOR_TOPIC_OTHER"
        };
        return topics[topic];
    };

    var showCheckboxGroupError = (form, names : string[]) : boolean => {
        var dirty = $scope.mercatorProposalForm.$submitted || _.some(names, (name) => form[name].$dirty);
        return !updateCheckBoxGroupValidity(form, names) && dirty;
    };

    $scope.showLocationError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalBriefForm, locationCheckboxes);
    };

    $scope.showStatusError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalBriefForm, locationCheckboxes);
    };

    $scope.showFinanceGrantedInfo = () : boolean => {
        return ($scope.data.finance && $scope.data.finance.other_sources && $scope.data.finance.other_sources !== "");
    };

    $scope.showHeardFromError = () : boolean => {
        return showCheckboxGroupError($scope.mercatorProposalCommunityForm, heardFromCheckboxes);
    };

    $scope.showError = adhShowError;

    // FIXME !
    $scope.create = "true";

    $scope.submitIfValid = () => {
        // // check validation of topics
        // $scope.topicChange(true);
        console.log(create($scope, adhPreliminaryNames));
    };

};
