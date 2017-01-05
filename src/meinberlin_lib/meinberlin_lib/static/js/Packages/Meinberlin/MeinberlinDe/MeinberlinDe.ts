/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../../Core/Config/Config";
import * as AdhTopLevelState from "../../Core/TopLevelState/TopLevelState";


var pkgLocation = "/Meinberlin/MeinberlinDe";


export var headerDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Header.html",
        scope: {},
        link: (scope) => {
            scope.hideHeader = adhConfig.hide_header;
            scope.$on("$destroy", adhTopLevelState.bind("areaHeaderSlot", scope));
        }
    };
};
