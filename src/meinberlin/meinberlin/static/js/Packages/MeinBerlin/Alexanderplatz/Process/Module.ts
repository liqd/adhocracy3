import AdhHttpModule = require("../../../Http/Module");
import AdhMovingColumnsModule = require("../../../MovingColumns/Module");
import AdhPermissionsModule = require("../../../Permissions/Module");
import AdhTabsModule = require("../../../Tabs/Module");
import AdhTopLevelStateModule = require("../../../TopLevelState/Module");

import AdhMeinBerlinPhaseModule = require("../../Phase/Module");

import AdhMeinBerlinAlexanderplatzProcess = require("./Process");


export var moduleName = "adhMeinBerlinAlexanderplatzProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhMeinBerlinPhaseModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhTabsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMeinBerlinAlexanderplatzPhaseHeader", [
            "adhConfig", "adhHttp", "adhTopLevelState", AdhMeinBerlinAlexanderplatzProcess.phaseHeaderDirective]);
};
