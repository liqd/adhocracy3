/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhHttp = require("../Http/Http");
import AdhUser = require("../User/User");


export class Service {
    constructor(private adhHttp : AdhHttp.Service<any>, private adhUser : AdhUser.Service) {}

    /**
     * Set result of OPTIONS request to scope.key and keep it fresh.
     * Before sending async http requests, initialize scope.key with
     * all-falses in order to avoid exceptions when scope.key is
     * accessed in javascript code (rather than ng templates).
     */
    public bindScope(scope : ng.IScope, path : string, key = "options") : ng.IPromise<void> {
        var self : Service = this;

        scope[key] = AdhHttp.emptyOptions;

        var update = () => {
            return self.adhHttp.options(path).then((options : AdhHttp.IOptions) => {
                scope[key] = options;
            });
        };

        // FIXME: It would be better if adhUser would notify us on change
        scope.$watch(() => self.adhUser.userPath, update);

        return update();
    }
}


export var moduleName = "adhPermissions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhUser.moduleName
        ])
        .service("adhPermissions", ["adhHttp", "adhUser", Service]);
};
