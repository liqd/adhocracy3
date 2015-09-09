import AdhTabs = require("./Tabs");


export var moduleName = "adhTabs";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("tabset", ["adhConfig", AdhTabs.tabsetDirective])
        .directive("tab", ["adhConfig", AdhTabs.tabDirective]);
};
