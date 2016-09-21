import * as Names from "./Names";

export var moduleName = "adhNames";


export var register = (angular) => {
    angular
        .module(moduleName, [])
        .provider("adhNames", Names.Provider);
};
