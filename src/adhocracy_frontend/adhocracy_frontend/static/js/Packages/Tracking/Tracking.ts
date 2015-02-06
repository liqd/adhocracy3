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
        private $q : ng.IQService,
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

    public setUser(userPath : string) {
        if (this.trackUserId) {
            this.$window._paq.push(["setUserId", userPath]);
        }
    }
}

export var moduleName = "adhTracking";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .service("adhTracking", ["$q", "$window", "adhConfig", Service]);
};
