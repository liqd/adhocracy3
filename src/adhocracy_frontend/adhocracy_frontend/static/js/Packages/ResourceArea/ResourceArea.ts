import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export interface Dict {
    [key : string]: string;
}


export class Provider implements ng.IServiceProvider {
    public $get;
    public defaults : {[key : string]: Dict};
    public specifics : {[key : string]: (resource) => any};  // values return either Dict or ng.IPromise<Dict>

    constructor() {
        var self = this;
        this.defaults = {};
        this.specifics = {};
        this.$get = ["$q", "$injector", "adhHttp", "adhConfig",
            ($q, $injector, adhHttp, adhConfig) => new Service(self, $q, $injector, adhHttp, adhConfig)];
    }

    public default(resourceType : string, view : string, defaults : Dict) : Provider {
        this.defaults[resourceType + "@" + view] = defaults;
        return this;
    }

    public specific(resourceType : string, view : string, factory : Function) : Provider;
    public specific(resourceType : string, view : string, factory : any[]) : Provider;
    public specific(resourceType, view, factory) {
        this.specifics[resourceType + "@" + view] = factory;
        return this;
    }
}


export class Service implements AdhTopLevelState.IAreaInput {
    public template : string = "<adh-page-wrapper><adh-platform></adh-platform></adh-page-wrapper>";

    constructor(
        private provider : Provider,
        private $q : ng.IQService,
        private $injector : ng.auto.IInjectorService,
        private adhHttp : AdhHttp.Service<any>,
        private adhConfig : AdhConfig.IService
    ) {}

    private getDefaults(resourceType : string, view : string) : Dict {
        return <Dict>_.extend({}, this.provider.defaults[resourceType + "@" + view]);
    }

    private getSpecifics(resource, view : string) : ng.IPromise<Dict> {
        var key = resource.content_type + "@" + view;
        var specifics;

        if (this.provider.specifics.hasOwnProperty(key)) {
            var factory = this.provider.specifics[key];
            var fn = this.$injector.invoke(factory);
            specifics = fn(resource);
        } else {
            specifics = {};
        }

        // fn may return a promise
        return this.$q.when(specifics)
            .then((data : Dict) => _.clone(data));
    }

    public route(path : string, search : Dict) : ng.IPromise<Dict> {
        var self : Service = this;
        var segs : string[] = path.replace(/\/+$/, "").split("/");

        if (segs.length < 2 || segs[0] !== "") {
            throw "bad path: " + path;
        }

        var view : string = "";

        // if path has a view segment
        if (_.last(segs).match(/^@/)) {
            view = segs.pop().replace(/^@/, "");
        }

        var resourceUrl : string = this.adhConfig.rest_url + segs.join("/");

        return this.adhHttp.get(resourceUrl).then((resource) => {
            return self.getSpecifics(resource, view).then((specifics : Dict) => {
                var defaults : Dict = self.getDefaults(resource.content_type, view);

                var meta : Dict = {
                    platform: segs[1],
                    contentType: resource.content_type,
                    resourceUrl: resource.path,
                    view: view
                };

                return _.extend(defaults, meta, specifics, search);
            });
        });
    }

    public reverse(data : Dict) : { path : string; search : Dict; } {
        var defaults = this.getDefaults(data["contentType"], data["view"]);
        var path = path = data["resourceUrl"].replace(this.adhConfig.rest_url, "");

        if (path.substr(-1) !== "/") {
            path += "/";
        }

        if (data["view"]) {
            path += "@" + data["view"];
        }

        return {
            path: path,
            search: _.transform(data, (result, value : string, key : string) => {
                if (defaults.hasOwnProperty(key) && value !== defaults[key]) {
                    result[key] = value;
                }
            })
        };
    }
}


export var platformDirective = (adhTopLevelState : AdhTopLevelState.Service) => {
    return {
        template:
            "<div data-ng-switch=\"platform\">" +
            "<div data-ng-switch-when=\"adhocracy\"><adh-document-workbench></div>" +
            // FIXME: move mercator specifics away
            "<div data-ng-switch-when=\"mercator\"><adh-mercator-workbench></div>" +
            "</div>",
        restrict: "E",
        link: (scope, element) => {
            adhTopLevelState.on("platform", (value : string) => {
                scope.platform = value;
            });
        }
    };
};


export var resourceUrl = (adhConfig : AdhConfig.IService) => {
    return (path : string, view? : string) => {
        if (typeof path !== "undefined") {
            var url = "/r" + path.replace(adhConfig.rest_url, "");
            if (typeof view !== "undefined") {
                url += "/@" + view;
            }
            return url;
        }
    };
};


export var moduleName = "adhResourceArea";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("r", ["adhResourceArea", (adhResourceArea : Service) => adhResourceArea]);
        }])
        .directive("adhPlatform", ["adhTopLevelState", platformDirective])
        .provider("adhResourceArea", Provider)
        .filter("adhResourceUrl", ["adhConfig", resourceUrl]);
};
