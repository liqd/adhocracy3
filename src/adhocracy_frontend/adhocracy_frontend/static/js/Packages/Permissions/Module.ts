import * as AdhCredentialsModule from "../User/Module";
import * as AdhHttpModule from "../Http/Module";

import * as AdhPermissions from "./Permissions";


export var moduleName = "adhPermissions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .service("adhPermissions", ["adhHttp", "adhCredentials", AdhPermissions.Service]);
};
