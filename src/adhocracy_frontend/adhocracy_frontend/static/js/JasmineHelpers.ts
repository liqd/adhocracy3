/// <reference path="../lib2/types/jasmine.d.ts"/>
/// <reference path="_all.d.ts"/>

import * as _ from "lodash";

export var customMatchers : jasmine.CustomMatcherFactories = {
    toSetEqual: function(util, customEqualityTesters) {

        return {
            compare: function(actual, expected) {

                var result = {
                    pass: util.equals(
                        _.uniq(_.sortBy(actual)),
                        _.uniq(_.sortBy(expected)),
                        customEqualityTesters
                    ),
                    message: undefined
                };

                if (result.pass) {
                    result.message = "Expected " + actual + " not to be set-equal to " + expected;
                } else {
                    result.message = "Expected " + actual + " to be set-equal to " + expected;
                }

                return result;
            }
        };
    }
};
