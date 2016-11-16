import * as AdhIdeaCollectionProcessModule from "./Process/Module";

export var moduleName = "adhIdeaCollection";

export var register = (angular) => {
    AdhIdeaCollectionProcessModule.register(angular);

    angular
        .module(moduleName, [
            AdhIdeaCollectionProcessModule.moduleName
        ]);
};
