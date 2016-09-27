/// <reference path="../../../../lib2/types/angular.d.ts"/>
/// <reference path="../../../../lib2/types/moment.d.ts"/>

import * as AdhConfig from "../Config/Config";

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
            moment.locale(config.locale);

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

