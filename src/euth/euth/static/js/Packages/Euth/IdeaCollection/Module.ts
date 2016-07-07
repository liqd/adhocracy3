import * as AdhEuthIdeaWorkbenchModule from "./Workbench/Module";

export var moduleName = "adhEuthIdeaCollection";

export var register = (angular) => {
    AdhEuthIdeaWorkbenchModule.register(angular);

    angular
        .module(moduleName, [
            AdhEuthIdeaWorkbenchModule.moduleName
        ]);
};
