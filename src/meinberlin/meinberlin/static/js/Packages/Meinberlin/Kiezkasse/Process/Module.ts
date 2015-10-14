import * as AdhHttpModule from "../../../Http/Module";
import * as AdhMovingColumnsModule from "../../../MovingColumns/Module";
import * as AdhPermissionsModule from "../../../Permissions/Module";
import * as AdhTabsModule from "../../../Tabs/Module";
import * as AdhTopLevelStateModule from "../../../TopLevelState/Module";

import * as AdhMeinberlinPhaseModule from "../../Phase/Module";

import * as Process from "./Process";


export var moduleName = "adhMeinberlinKiezkasseProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhMeinberlinPhaseModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhTabsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMeinberlinKiezkassePhaseHeader", ["adhConfig", "adhHttp", "adhTopLevelState", Process.phaseHeaderDirective])
        .directive("adhMeinberlinKiezkasseDetail", ["adhConfig", "adhHttp", "adhPermissions", Process.detailDirective])
        .directive("adhMeinberlinKiezkasseEdit", [
            "adhConfig", "adhHttp", "adhShowError", "adhSubmitIfValid", "moment", Process.editDirective]);
};
