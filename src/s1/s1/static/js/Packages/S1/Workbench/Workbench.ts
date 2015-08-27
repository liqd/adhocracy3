/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../../Config/Config");
import AdhProcess = require("../../Process/Process");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");

import RIS1Process = require("../../../Resources_/adhocracy_s1/resources/s1/IProcess");

var pkgLocation = "/S1/Workbench";


export var s1WorkbenchDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
        }
    };
};


export var registerRoutes = (
    processType : string = "",
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider
        .default(RIS1Process, "", processType, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        });
};


export var moduleName = "adhS1Workbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhProcess.moduleName,
            AdhResourceArea.moduleName
        ])
        .config(["adhResourceAreaProvider", registerRoutes(RIS1Process.content_type)])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[RIS1Process.content_type] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-s1-workbench></adh-s1-workbench>");
            }];
        }])
        .directive("adhS1Workbench", ["adhConfig", s1WorkbenchDirective]);
};
