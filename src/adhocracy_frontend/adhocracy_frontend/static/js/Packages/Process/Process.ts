/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export class Provider implements angular.IServiceProvider {
    public templateFactories : {[processType : string]: Function};
    public $get;

    constructor () {
        this.templateFactories = {};

        this.$get = ["$injector", ($injector) => {
            return new Service(this, $injector);
        }];
    }
}

export class Service {
    constructor(
        private provider : Provider,
        private $injector : angular.auto.IInjectorService
    ) {}

    public getTemplate(processType : string) : angular.IPromise<string> {
        var fn = this.provider.templateFactories[processType];
        return this.$injector.invoke(fn);
    }
}

export var processViewDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhProcess : Service,
    $compile : angular.ICompileService
) => {
    return {
        restrict: "E",
        link: (scope, element) => {
            adhTopLevelState.on("processType", (processType) => {
                if (typeof processType !== "undefined") {
                    adhProcess.getTemplate(processType).then((template) => {
                        element.html(template);
                        $compile(element.contents())(scope);
                    });
                }
            });
        }
    };
};


export var moduleName = "adhProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        .provider("adhProcess", Provider)
        .directive("adhProcessView", ["adhTopLevelState", "adhProcess", "$compile", processViewDirective]);
};
