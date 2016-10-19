/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhHttp from "../Http/Http";

import * as AdhCredentials from "./Credentials";

import RIUser from "../../../Resources_/adhocracy_core/resources/principal/IUser";
import * as SIAnonymizeDefault from "../../../Resources_/adhocracy_core/sheets/principal/IAnonymizeDefault";
import * as SIPasswordAuthentication from "../../../Resources_/adhocracy_core/sheets/principal/IPasswordAuthentication";
import * as SIUserBasic from "../../../Resources_/adhocracy_core/sheets/principal/IUserBasic";
import * as SIUserExtended from "../../../Resources_/adhocracy_core/sheets/principal/IUserExtended";
import * as SICaptcha from "../../../Resources_/adhocracy_core/sheets/principal/ICaptcha";


export interface IUserBasic {
    name? : string;
    tzname? : string;
}


export interface IRegisterResponse {}


export class Service {
    public data : {
        name : string;
        anonymize : boolean;
    };
    public ready : angular.IPromise<RIUser>;

    constructor(
        private adhHttp : AdhHttp.Service,
        private adhCredentials : AdhCredentials.Service,
        private $q : angular.IQService,
        private $rootScope : angular.IScope
    ) {
        var _self : Service = this;

        var deferred = _self.$q.defer();
        _self.ready = deferred.promise;

        _self.adhCredentials.ready.then(() => {
            _self.$rootScope.$watch(() => _self.adhCredentials.userPath, ((userPath) => {
                if (userPath) {
                    _self.loadUser(userPath).then(() => {
                        deferred.resolve(_self.data);
                    });
                } else {
                    _self.data = undefined;
                    deferred.resolve(null);
                }
            }));
        });
    }

    public loadUser(userPath) {
        var _self : Service = this;

        return _self.adhHttp.get(userPath)
            .then((resource) => {
                _self.data = {
                    name: resource.data[SIUserBasic.nick].name,
                    anonymize: resource.data[SIAnonymizeDefault.nick].anonymize,
                };
            }, (reason) => {
                // The user resource that was returned by the server could not be accessed.
                // This may happen e.g. with a network disconnect

                // FIXME: The request might fail because the window is
                // closed. In that case there is no reason to delete
                // the token. We need to be able to discern the two
                // cases.
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

    public register(username : string, email : string, password : string, passwordRepeat : string,
                    captchaId : string, captchaGuess : string) : angular.IPromise<IRegisterResponse> {
        var _self : Service = this;

        var resource = {
            "content_type": "adhocracy_core.resources.principal.IUser",
            "data": {}
        };
        SIUserBasic.set(resource, {
            "name": username
        });
        SIUserExtended.set(resource, {
            "email": email
        });
        SIPasswordAuthentication.set(resource, {
            "password": password
        });
        if (captchaId && captchaGuess) {
            SICaptcha.set(resource, {
                "id": captchaId,
                "solution": captchaGuess
            });
        }

        return _self.adhHttp.post("/principals/users/", resource, {
            noExport: true
        });
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
