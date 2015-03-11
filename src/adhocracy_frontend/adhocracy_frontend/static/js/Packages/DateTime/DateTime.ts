/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import AdhConfig = require("../Config/Config");

/**
 * A wrapper around HTML5's <time> integrating moment.js.
 */
export var createDirective = (config : AdhConfig.IService, moment : moment.MomentStatic, $interval : angular.IIntervalService) => {
    return {
        restrict: "E",
        template: "<time datetime=\"{{datetimeString}}\">{{text}}</time>",
        scope: {
            datetime: "=",
            format: "@?"
        },
        link: (scope) => {
            (<any>moment).locale(config.locale);

            var intervalPromise;

            scope.$watch("datetime", (datetime) => {
                if (typeof intervalPromise !== "undefined") {
                    $interval.cancel(intervalPromise);
                }

                var dt = moment(datetime);

                scope.datetimeString = dt.format();

                if (typeof scope.format !== "undefined") {
                    scope.text = dt.format(scope.format);
                } else {
                    scope.text = dt.fromNow();

                    intervalPromise = $interval(() => {
                        scope.text = dt.fromNow();
                    }, 5000);
                }
            });
        }
    };
};


export var moduleName = "adhDateTime";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhTime", ["adhConfig", "moment", "$interval", createDirective]);
};
