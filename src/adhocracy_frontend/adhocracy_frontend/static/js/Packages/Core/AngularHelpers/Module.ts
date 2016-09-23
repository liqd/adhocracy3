import * as angularScroll from "angularScroll";  if (angularScroll) { ; };

import * as AdhHttpModule from "../Http/Module";

import * as AdhAngularHelpers from "./AngularHelpers";


export var moduleName = "adhAngularHelpers";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            AdhHttpModule.moduleName
        ])
        .filter("join", () => (list : any[], separator : string = ", ") : string => list.join(separator))
        .filter("signum", () => (n : number) : string => (typeof n === "number") ? (n > 0 ? "+" + n.toString() : n.toString()) : "0")
        .filter("percentage", () => (i : number, t : number) : string => Math.round((i / t) * 100).toString() + "%")
        .filter("numberOrDash", () => AdhAngularHelpers.numberOrDashFilter)
        .factory("adhRecursionHelper", ["$compile", AdhAngularHelpers.recursionHelper])
        .factory("adhShowError", () => AdhAngularHelpers.showError)
        .factory("adhSingleClickWrapper", ["$timeout", AdhAngularHelpers.singleClickWrapperFactory])
        .factory("adhSubmitIfValid", ["$q", AdhAngularHelpers.submitIfValid])
        .directive("adhRecompileOnChange", ["$compile", AdhAngularHelpers.recompileOnChange])
        .directive("adhWait", AdhAngularHelpers.waitForCondition)
        .directive("adhInputSync", ["$timeout" , AdhAngularHelpers.inputSync]);
};
