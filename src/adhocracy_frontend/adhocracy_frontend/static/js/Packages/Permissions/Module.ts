import AdhCredentialsModule = require("../User/Module");
import AdhHttpModule = require("../Http/Module");

import AdhPermissions = require("./Permissions");


export var moduleName = "adhPermissions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .service("adhPermissions", ["adhHttp", "adhCredentials", AdhPermissions.Service]);
};
