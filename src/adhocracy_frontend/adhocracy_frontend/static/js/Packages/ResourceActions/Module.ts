import * as AdhMovingColumnsModule from "../MovingColumns/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";

import * as AdhResourceActions from "./ResourceActions";

export var moduleName = "adhResourceActions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelStateModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhMovingColumnsModule.moduleName
        ])
        .directive("adhResourceActions", ["adhPermissions", "adhConfig", AdhResourceActions.resourceActionsDirective])
        .directive("adhReportAction", ["adhConfig", AdhResourceActions.reportActionDirective])
        .directive("adhCancelAction", ["adhConfig", "adhTopLevelState", "adhResourceUrlFilter", AdhResourceActions.cancelActionDirective]);
};
