/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../Config/Config");

export interface PiwikWindow extends Window {
    _paq : any[];
}

export class Service {
    private trackingEnabled : boolean;
    private trackUserId : boolean;
    private _paq : any[];

    constructor(
        private $q : angular.IQService,
        private $window : PiwikWindow,
        private adhConfig : AdhConfig.IService
    ) {
        this.trackingEnabled = !!adhConfig.piwik_enabled;
        this.trackUserId = !!adhConfig.piwik_track_user_id;

        if (this.trackingEnabled) {
            this._paq = [];
            $window._paq = this._paq;

            // Setup piwik
            this.$window._paq.push(["setSiteId", adhConfig.piwik_site_id]);
            this.$window._paq.push(["setTrackerUrl", adhConfig.piwik_host + "piwik.php"]);

            if (!adhConfig.piwik_use_cookies) {
                this.$window._paq.push(["disableCookies"]);
            }

            // Load piwik
            $.ajax({
                url: adhConfig.piwik_host + "piwik.js",
                dataType: "script",
                success: () => {
                    console.log(
                        "piwik loaded from " + adhConfig.piwik_host
                        + " with cookies " + (!!adhConfig.piwik_use_cookies ? "enabled" : "disabled"));
                }
            });
        }
    }

    public trackPageView(url : string, title? : string) {
        if (this.trackingEnabled) {
            this.$window._paq.push(["trackLink", url, "link"]);
        }
    }

    public setLoginState(loggedIn : boolean) {
        if (this.trackingEnabled) {
            // NOTE: tracking login state on a page base
            this.setCustomVariable(1, "user type", loggedIn ? "registered" : "anonymous", "page");
        }
    }

    public setUserId(userPath : string) {
        if (this.trackingEnabled && this.trackUserId) {
            this.$window._paq.push(["setUserId", userPath]);
        }
    }

    /* TODO: nicer API without explicit index argument */
    private setCustomVariable(index : number, name : string, value : string, scope : string) {
        this.$window._paq.push(["setCustomVariable", index, name, value, scope]);
    }

}

export var moduleName = "adhTracking";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .service("adhTracking", ["$q", "$window", "adhConfig", Service]);
};
