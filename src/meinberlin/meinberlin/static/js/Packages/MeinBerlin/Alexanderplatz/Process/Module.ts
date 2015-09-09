import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhTabsModule from "../../../Tabs/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinBerlinPhaseModule from "../../Phase/Module";

import * as AdhMeinBerlinAlexanderplatzProcess from "./Process";


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
