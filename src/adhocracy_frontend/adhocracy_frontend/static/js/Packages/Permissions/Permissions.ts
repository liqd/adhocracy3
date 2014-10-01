/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhHttp = require("../Http/Http");
import AdhUser = require("../User/User");


export class Service {
    constructor(private adhHttp : AdhHttp.Service<any>, private adhUser : AdhUser.User) {}

    /**
     * Set result of OPTIONS request to scope.key and keep it fresh.
     */
    public bindScope(scope : ng.IScope, path : string, key = "options") : ng.IPromise<void> {
        return this.adhHttp.options(path).then((options) => {
            scope[key] = options;
        });
    }
}
