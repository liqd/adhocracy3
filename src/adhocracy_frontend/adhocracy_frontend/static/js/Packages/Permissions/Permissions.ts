/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhCredentials = require("../User/Credentials");
import AdhHttp = require("../Http/Http");


export class Service {
    constructor(private adhHttp : AdhHttp.Service<any>, private adhCredentials : AdhCredentials.Service) {}

    /**
     * Set result of OPTIONS request to scope.key and keep it fresh.
     * Before sending async http requests, initialize scope.key with
     * all-falses in order to avoid exceptions when scope.key is
     * accessed in javascript code (rather than ng templates).
     */
    public bindScope(scope : angular.IScope, path : Function, key?) : void;
    public bindScope(scope : angular.IScope, path : string, key?) : void;
    public bindScope(scope, path, key = "options") {
        var self : Service = this;

        var pathFn = typeof path === "string" ? () => path : path;
        var pathString : string;

        scope[key] = AdhHttp.emptyOptions;

        var update = () => {
            if (pathString) {
                return self.adhHttp.options(pathString).then((options : AdhHttp.IOptions) => {
                    scope[key] = options;
                });
            }
        };

        // FIXME: It would be better if adhCredentials would notify us on change
        scope.$watch(() => self.adhCredentials.userPath, update);
        scope.$watch(pathFn, (p : string) => {
            pathString = p;
            update();
        });
    }
}


export var moduleName = "adhPermissions";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentials.moduleName,
            AdhHttp.moduleName
        ])
        .service("adhPermissions", ["adhHttp", "adhCredentials", Service]);
};
