/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import * as AdhConfig from "../../../Config/Config";

var pkgLocation = "/Mercator/2016/Proposal";


export interface IData {
    user_info : {
        first_name : string;
        last_name : string;
    };
    organization_info : {
        name : string;
        email : string;
        website : string;
        city : string;
        country : string;
        status_enum : string;
        status_other : string;
        date_of_foreseen_registration : string;
        date_of_registration : string;
        how_can_we_help_you : string;
    };
    title : string;
    introduction : {
        teaser : string;
        imageUpload : any;
        picture : any;
    };
    partners : boolean;
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
    morePartners : boolean;
    partners_more : string;
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
        aim : string;
        plan : string;
        targetgroup : string;
        team : string;
        whatelse : string;
    };
    criteria : {
        strengthen : string;
        different : string;
        practical : string;
    };
    finance : {
        budget : number;
        requested_funding : number;
        major : string;
        other_sources : string;
        secured : boolean;
        experience : string;
    };
    heardFrom : {
        facebook : boolean;
        newsletter : boolean;
        other : boolean;
        other_specify : string;
        personal_contact : boolean;
        twitter : boolean;
        website : boolean;
    };
    acceptDisclaimer : boolean;
}


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
    adhShowError
) => {

    $scope.data = {};

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
        return ("TR__MERCATOR_TOPIC_" + topic.toUpperCase());
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
        // check validation of topics
        $scope.topicChange(true);
    };

};
