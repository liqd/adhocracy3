/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export class Provider implements angular.IServiceProvider {
    public templateUrls : {[processType : string]: string};
    public $get;

    constructor () {
        this.templateUrls = {};

        this.$get = ["$templateRequest", ($templateRequest) => {
            return new Service(this, $templateRequest);
        }];
    }
}

export class Service {
    constructor(
        private provider : Provider,
        private $templateRequest : angular.ITemplateRequestService
    ) {}

    public getTemplate(processType : string) : angular.IPromise<string> {
        var templateUrl = this.provider.templateUrls[processType];
        return this.$templateRequest(templateUrl);
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
                adhProcess.getTemplate(processType).then((template) => {
                    element.html(template);
                    $compile(element.contents())(scope);
                });
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
