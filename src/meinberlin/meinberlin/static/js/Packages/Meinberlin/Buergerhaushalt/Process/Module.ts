import * as AdhHttpModule from "../../../Http/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinberlinBuergerhaushaltProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName
        ])
        .directive("adhMeinberlinBuergerhaushaltDetail", ["adhConfig", "adhHttp", "adhPermissions", Process.detailDirective]);
};
