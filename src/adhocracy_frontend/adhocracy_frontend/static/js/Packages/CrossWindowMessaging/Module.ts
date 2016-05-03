import * as AdhCredentialsModule from "../User/Module";
import * as AdhUserModule from "../User/Module";

import * as AdhCrossWindowMessaging from "./CrossWindowMessaging";


export var moduleName = "adhCrossWindowMessaging";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhUserModule.moduleName
        ])
        .provider("adhCrossWindowMessaging", AdhCrossWindowMessaging.Provider);
};
