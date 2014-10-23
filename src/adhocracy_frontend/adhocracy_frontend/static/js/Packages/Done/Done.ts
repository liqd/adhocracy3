/**
 * This service is just a dummy callback.  You can use it wherever
 * dependency injection is used and where you want to be able to inject
 * a real callback in your tests.
 */
export var moduleName = "adhDone";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .value("adhDone", () => null);
};
