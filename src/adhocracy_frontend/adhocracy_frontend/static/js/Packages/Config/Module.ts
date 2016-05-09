export var moduleName = "AdhConfig";

export var register = (angular, data) => {
    angular
        .module(moduleName, [])
        .constant("adhConfig", data);
};
