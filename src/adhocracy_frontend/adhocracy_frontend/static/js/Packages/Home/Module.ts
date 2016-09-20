import * as Home from "./Home";

export var moduleName = "adhHome";


export var register = (angular) => {
    angular.module(moduleName, [
    ])
    .directive("adhHome", ["adhConfig", Home.homeDirective]);
};
