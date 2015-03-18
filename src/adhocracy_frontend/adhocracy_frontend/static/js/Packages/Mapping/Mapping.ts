export var mapinput = () => {
    return {
        scope: {

        },
        restrict: "E",
        replace: true,
        template: "<div></div>"
    };
};

export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("mapinput", [mapinput]);
};
