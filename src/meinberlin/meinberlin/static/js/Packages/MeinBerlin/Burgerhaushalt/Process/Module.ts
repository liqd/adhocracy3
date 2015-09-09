import AdhHttpModule = require("../../../Http/Module");
import AdhMovingColumnsModule = require("../../../MovingColumns/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinPhaseModule = require("../../Phase/Module");

import Process = require("./Process");


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
