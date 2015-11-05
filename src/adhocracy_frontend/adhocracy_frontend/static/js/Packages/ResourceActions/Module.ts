import * as AdhTopLevelStateModule from "../TopLevelState/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";

import * as AdhResourceActions from "./ResourceActions";

export var moduleName = "adhResourceActions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelStateModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .directive("adhResourceActions", ["adhPermissions", "adhConfig", AdhResourceActions.resourceActionsDirective])
        .directive("adhCancel", ["adhConfig", "adhTopLevelState", "adhResourceUrlFilter", AdhResourceActions.cancelDirective]);
};
