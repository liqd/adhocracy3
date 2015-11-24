/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/moment/moment.d.ts"/>

import * as AdhConfig from "../Config/Config";

var pkgLocation = "/MercatorProposal2016";

export var createDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/create.html",
        scope: {},
        link: (scope) => {
            console.log(scope);

        }
    };
};
