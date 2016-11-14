import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhPreliminaryNamesModule from "../../../Core/PreliminaryNames/Module";
import * as AdhAngularHelpers from "../../../Core/AngularHelpers/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinBerlinBplanProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhHttpModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
        ])
        .directive("adhMeinberlinBplanProcessCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", "$window", Process.createDirective]);
};
