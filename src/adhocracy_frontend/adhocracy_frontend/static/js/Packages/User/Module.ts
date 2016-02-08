import * as AdhHttpModule from "../Http/Module";
import * as AdhCredentialsModule from "./CredentialsModule";

import * as AdhUser from "./User";


export var moduleName = "adhUser";

export var register = (angular) => {
    AdhCredentialsModule.register(angular);

    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .service("adhUser", ["adhHttp", "adhCredentials", "$q", "$rootScope", AdhUser.Service]);
};
