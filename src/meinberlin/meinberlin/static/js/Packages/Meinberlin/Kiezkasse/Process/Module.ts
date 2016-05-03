import * as AdhHttpModule from "../../../Http/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinberlinKiezkasseProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhPermissionsModule.moduleName
        ])
        .directive("adhMeinberlinKiezkasseDetail", ["adhConfig", "adhHttp", "adhPermissions", Process.detailDirective])
        .directive("adhMeinberlinKiezkasseEdit", [
            "adhConfig", "adhHttp", "adhShowError", "adhSubmitIfValid", "moment", Process.editDirective]);
};
