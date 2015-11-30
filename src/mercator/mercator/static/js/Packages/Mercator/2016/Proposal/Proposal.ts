/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import * as AdhConfig from "../../../Config/Config";

var pkgLocation = "/Mercator/2016/Proposal";


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

export var mercatorProposalFormController2016 = ($scope, $element, $window, adhShowError) => {
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

    $scope.topicChange = (elem) => {
        topicTotal = elem ? (topicTotal + 1) : (topicTotal - 1);
        console.log($scope);
        $scope.mercatorProposalForm.mercatorProposalIntroductionForm.$setValidity("enoughTopics", (topicTotal >= 2));
    };

    $scope.topicTrString = (topic) => {
        return ("TR__MERCATOR_TOPIC_" + topic.toUpperCase());
    };
};
