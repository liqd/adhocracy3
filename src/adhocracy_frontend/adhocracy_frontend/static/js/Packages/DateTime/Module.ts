import AdhDateTime = require("./DateTime");


export var moduleName = "adhDateTime";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhTime", ["adhConfig", "moment", "$interval", AdhDateTime.createDirective]);
};
