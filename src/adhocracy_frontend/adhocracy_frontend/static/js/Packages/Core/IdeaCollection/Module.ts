import * as AdhIdeaCollectionPollModule from "./Poll/Module";
import * as AdhIdeaCollectionProcessModule from "./Process/Module";

export var moduleName = "adhIdeaCollection";

export var register = (angular) => {
    AdhIdeaCollectionPollModule.register(angular);
    AdhIdeaCollectionProcessModule.register(angular);

    angular
        .module(moduleName, [
            AdhIdeaCollectionPollModule.moduleName,
            AdhIdeaCollectionProcessModule.moduleName
        ]);
};
