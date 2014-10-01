/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhHttp = require("../Http/Http");
import AdhUser = require("../User/User");


export class Service {
    constructor(private adhHttp : AdhHttp.Service<any>, private adhUser : AdhUser.User) {}

    /**
     * Set result of OPTIONS request to scope.key and keep it fresh.
     */
    public bindScope(scope : ng.IScope, path : string, key = "options") : ng.IPromise<void> {
        var self : Service = this;

        var update = () => {
            return self.adhHttp.options(path).then((options) => {
                scope[key] = options;
            });
        };

        // FIXME: It would be better if adhUser would notify us on change
        scope.$watch(() => self.adhUser.userPath, update);

        return update();
    }
}
