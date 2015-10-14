import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinberlinPhaseModule from "../../Phase/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinberlinBuergerhaushaltProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhMeinberlinPhaseModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMeinberlinBuergerhaushaltPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", Process.phaseHeaderDirective])
        .directive("adhMeinberlinBuergerhaushaltDetail", ["adhConfig", "adhHttp", "adhPermissions", Process.detailDirective]);
};
