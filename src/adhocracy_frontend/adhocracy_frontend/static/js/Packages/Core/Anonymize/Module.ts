import * as AdhHttpModule from "../Http/Module";
import * as AdhUserModule from "../User/Module";

import * as AdhAnonymize from "./Anonymize";


export var moduleName = "adhAnonymize";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhUserModule.moduleName
        ])
        .directive("adhAnonymize", ["adhConfig", "adhHttp", "adhUser", "$q", AdhAnonymize.anonymizeDirective]);
};
