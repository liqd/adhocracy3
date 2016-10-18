/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhCredentials from "../User/Credentials";
import * as AdhHttp from "../Http/Http";


export class Service {
    constructor(private adhHttp : AdhHttp.Service, private adhCredentials : AdhCredentials.Service) {}

    /**
     * Set result of OPTIONS request to scope.key and keep it fresh.
     * Before sending async http requests, initialize scope.key with
     * all-falses in order to avoid exceptions when scope.key is
     * accessed in javascript code (rather than ng templates).
     */
    public bindScope(scope : angular.IScope, path : Function, key?, config? : {}) : void;
    public bindScope(scope : angular.IScope, path : string, key?, config? : {}) : void;
    public bindScope(scope, path, key = "options", config = {}) {
        var self : Service = this;

        var pathFn = typeof path === "string" ? () => path : path;
        var pathString : string;

        scope[key] = _.assign({}, AdhHttp.emptyOptions, {"loggedIn": self.adhCredentials.loggedIn});

        var update = () => {
            if (pathString) {
                return self.adhHttp.options(pathString, config).then((options : AdhHttp.IOptions) => {
                    scope[key] = _.assign({}, options, {"loggedIn": self.adhCredentials.loggedIn});
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
