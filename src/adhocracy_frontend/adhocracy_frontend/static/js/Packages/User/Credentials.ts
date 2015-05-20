/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhCache = require("../Http/Cache");
import AdhConfig = require("../Config/Config");
import AdhTracking = require("../Tracking/Tracking");


export class Service {
    public token : string;
    public userPath : string;
    public loggedIn : boolean;
    public ready : angular.IPromise<boolean>;

    constructor(
        private adhConfig : AdhConfig.IService,
        private adhCache : AdhCache.Service,
        private adhTracking : AdhTracking.Service,
        private Modernizr,
        private ng : typeof angular,
        private $q : angular.IQService,
        private $http : angular.IHttpService,
        private $timeout : angular.ITimeoutService,
        private $rootScope : angular.IScope,
        private $window
    ) {
        var _self : Service = this;

        var deferred = $q.defer();
        _self.ready = deferred.promise;
        var unwatch = _self.$rootScope.$watch(() => _self.loggedIn, ((loggedIn) => {
            if (typeof loggedIn !== "undefined") {
                deferred.resolve(loggedIn);
                unwatch();
            }
        }));

        if (_self.Modernizr.localstorage) {
            var sessionValue = _self.$window.localStorage.getItem("user-session");
            _self.updateSessionFromStorage(sessionValue);

            _self.ng.element(_self.$window).on("storage", (event) => {
                var storageEvent = <any>event.originalEvent;
                if (storageEvent.key === "user-session") {
                    _self.updateSessionFromStorage(storageEvent.newValue);
                }
            });
        } else {
            _self.loggedIn = false;
        }
    }

    private updateSessionFromStorage(sessionValue) : angular.IPromise<boolean> {
        var _self : Service = this;

        var deferred = _self.$q.defer();

        if (sessionValue) {
            try {
                var session = JSON.parse(sessionValue);
                var path = session["user-path"];
                var token = session["user-token"];
                _self.$http.head(_self.adhConfig.rest_url, {
                    headers: {
                        "X-User-Token": token,
                        "X-User-Path": path
                    }
                }).then((response) => {
                    _self.enableToken(token, path);
                    deferred.resolve(true);
                }, (msg) => {
                    console.log("Expired or invalid session deleted");
                    _self.deleteToken();
                    deferred.resolve(false);
                });
            } catch (e) {
                console.log("Invalid session deleted");
                _self.deleteToken();
                deferred.resolve(false);
            }
        } else {
            _self.$timeout(() => {
                _self.deleteToken();
                deferred.resolve(false);
            });
        }

        return deferred.promise;
    }

    private enableToken(token : string, userPath : string) : void {
        this.token = token;
        this.userPath = userPath;
        this.loggedIn = true;
        this.$http.defaults.headers.common["X-User-Token"] = token;
        this.$http.defaults.headers.common["X-User-Path"] = userPath;
        this.adhTracking.setLoginState(true);
        this.adhTracking.setUserId(userPath);
    }

    public storeAndEnableToken(token : string, userPath : string) : void {
        if (this.Modernizr.localstorage) {
            this.$window.localStorage.setItem("user-session", JSON.stringify({
                "user-path": userPath,
                "user-token": token
            }));
        } else {
            console.log("session could not be persisted");
        }

        return this.enableToken(token, userPath);
    }

    public deleteToken() : void {
        if (this.Modernizr.localstorage) {
            this.$window.localStorage.removeItem("user-session");
        }
        delete this.$http.defaults.headers.common["X-User-Token"];
        delete this.$http.defaults.headers.common["X-User-Path"];
        this.token = undefined;
        this.userPath = undefined;
        this.loggedIn = false;
        this.adhTracking.setLoginState(false);
        this.adhTracking.setUserId(null);

        this.adhCache.invalidateAll();
    }
}


export var moduleName = "adhCredentials";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTracking.moduleName
        ])
        .service("adhCredentials", [
            "adhConfig", "adhCache", "adhTracking", "Modernizr", "angular", "$q", "$http", "$timeout", "$rootScope", "$window", Service]);
};
