import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinBerlinPhaseModule from "../../Phase/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinBerlinBurgerhaushaltProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhMeinBerlinPhaseModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMeinBerlinBurgerhaushaltPhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", Process.phaseHeaderDirective])
        .directive("adhMeinBerlinBurgerhaushaltDetail", ["adhConfig", "adhHttp", "adhPermissions", Process.detailDirective]);
};
