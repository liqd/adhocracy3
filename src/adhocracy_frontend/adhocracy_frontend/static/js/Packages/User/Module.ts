import AdhHttpModule = require("../Http/Module");
import AdhCredentialsModule = require("./CredentialsModule");

import AdhUser = require("./User");


export var moduleName = "adhUser";

export var register = (angular) => {
    AdhCredentialsModule.register(angular);

    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .service("adhUser", ["adhHttp", "adhCredentials", "$rootScope", AdhUser.Service]);
};
