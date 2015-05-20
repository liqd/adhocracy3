/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhHttp = require("../Http/Http");

import AdhCredentials = require("./Credentials");

import SIPasswordAuthentication = require("../../Resources_/adhocracy_core/sheets/principal/IPasswordAuthentication");
import SIUserBasic = require("../../Resources_/adhocracy_core/sheets/principal/IUserBasic");
import SIUserExtended = require("../../Resources_/adhocracy_core/sheets/principal/IUserExtended");


export interface IUserBasic {
    name? : string;
    tzname? : string;
}


export interface IRegisterResponse {}


export class Service {
    public data : IUserBasic;

    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private adhCredentials : AdhCredentials.Service,
        private $rootScope : angular.IScope
    ) {
        var _self : Service = this;

        _self.$rootScope.$watch(() => adhCredentials.userPath, (userPath) => {
            if (userPath) {
                _self.loadUser(userPath);
            } else {
                _self.data = undefined;
            }
        });
    }

    private loadUser(userPath) {
        var _self : Service = this;

        return _self.adhHttp.get(userPath)
            .then((resource) => {
                _self.data = resource.data[SIUserBasic.nick];
            }, (reason) => {
                // The user resource that was returned by the server could not be accessed.
                // This may happen e.g. with a network disconnect
                _self.adhCredentials.deleteToken();
                throw "failed to fetch user resource";
            });
    }

    public logIn(nameOrEmail : string, password : string) : angular.IPromise<void> {
        var _self : Service = this;
        var promise;

        if (nameOrEmail.indexOf("@") === -1) {
            promise = _self.adhHttp.postRaw("/login_username", {
                name: nameOrEmail,
                password: password
            });
        } else {
            promise = _self.adhHttp.postRaw("/login_email", {
                email: nameOrEmail,
                password: password
            });
        }

        var success = (response) => {
            return _self.adhCredentials.storeAndEnableToken(response.data.user_token, response.data.user_path);
        };

        return promise
            .then(success, AdhHttp.logBackendError);
    }

    public logOut() : void {
        // The server does not have a logout yet.
        this.adhCredentials.deleteToken();
    }

    public register(username : string, email : string, password : string, passwordRepeat : string) : angular.IPromise<IRegisterResponse> {
        var _self : Service = this;

        var resource = {
            "content_type": "adhocracy_core.resources.principal.IUser",
            "data": {}
        };
        resource.data[SIUserBasic.nick] = {
            "name": username
        };
        resource.data[SIUserExtended.nick] = {
            "email": email
        };
        resource.data[SIPasswordAuthentication.nick] = {
            "password": password
        };

        return _self.adhHttp.post("/principals/users/", resource);
    }

    public activate(path : string) : angular.IPromise<void> {
        var _self : Service = this;

        var success = (response) => {
            return _self.adhCredentials.storeAndEnableToken(response.data.user_token, response.data.user_path);
        };

        return _self.adhHttp.postRaw("/activate_account", {path: path})
            .then(success, AdhHttp.logBackendError);
    }

    public passwordReset(path : string, password : string) : angular.IPromise<any> {
        var _self : Service = this;

        var success = (response) => {
            return _self.adhCredentials.storeAndEnableToken(response.data.user_token, response.data.user_path);
        };

        return _self.adhHttp.postRaw("/password_reset", {
            path: path,
            password: password
        }).then(success, AdhHttp.logBackendError);
    }
}


export var moduleName = "adhUser";

export var register = (angular) => {
    AdhCredentials.register(angular);

    angular
        .module(moduleName, [
            AdhCredentials.moduleName,
            AdhHttp.moduleName
        ])
        .service("adhUser", ["adhHttp", "adhCredentials", "$rootScope", Service]);
};
