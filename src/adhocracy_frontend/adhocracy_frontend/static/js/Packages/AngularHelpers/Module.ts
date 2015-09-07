import AdhHttpModule = require("../Http/Module");

import AdhAngularHelpers = require("./AngularHelpers");


export var moduleName = "adhAngularHelpers";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            AdhHttpModule.moduleName
        ])
        .filter("join", () => (list : any[], separator : string = ", ") : string => list.join(separator))
        .filter("signum", () => (n : number) : string => (typeof n === "number") ? (n > 0 ? "+" + n.toString() : n.toString()) : "0")
        .factory("adhRecursionHelper", ["$compile", AdhAngularHelpers.recursionHelper])
        .factory("adhShowError", () => AdhAngularHelpers.showError)
        .factory("adhSingleClickWrapper", ["$timeout", AdhAngularHelpers.singleClickWrapperFactory])
        .factory("adhSubmitIfValid", ["$q", AdhAngularHelpers.submitIfValid])
        .directive("adhRecompileOnChange", ["$compile", AdhAngularHelpers.recompileOnChange])
        .directive("adhLastVersion", ["$compile", "adhHttp", AdhAngularHelpers.lastVersion])
        .directive("adhWait", AdhAngularHelpers.waitForCondition)
        .directive("adhInputSync", ["$timeout" , AdhAngularHelpers.inputSync]);
};
