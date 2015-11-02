import * as AdhResourceActions from "./ResourceActions";

export var moduleName = "adhResourceActions";

export var register = (angular) => {
    angular
        .module(moduleName, [

        ])
        .directive("adhResourceActions", ["adhPermissions", "adhConfig", AdhResourceActions.resourceActions]);
};