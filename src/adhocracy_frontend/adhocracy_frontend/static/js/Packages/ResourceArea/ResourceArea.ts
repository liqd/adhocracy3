import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");

import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhProcess = require("../Process/Process");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

var pkgLocation = "/ResourceArea";


export interface Dict {
    [key : string]: string;
}


export class Provider implements angular.IServiceProvider {
    public $get;
    public defaults : {[key : string]: Dict};
    public specifics : {[key : string]: (resource) => any};  // values return either Dict or angular.IPromise<Dict>

    constructor() {
        var self = this;
        this.defaults = {};
        this.specifics = {};
        this.$get = ["$q", "$injector", "$location", "adhHttp", "adhConfig", "adhResourceUrlFilter",
            ($q, $injector, $location, adhHttp, adhConfig, adhResourceUrlFilter) => new Service(
        self, $q, $injector, $location, adhHttp, adhConfig, adhResourceUrlFilter)];
    }

    public default(resourceType : string, view : string, processType : string, defaults : Dict) : Provider {
        var key : string = resourceType + "@" + view + "@" + processType;
        this.defaults[key] = defaults;
        return this;
    }

    public specific(resourceType : string, view : string, processType : string, factory : Function) : Provider;
    public specific(resourceType : string, view : string, processType : string, factory : any[]) : Provider;
    public specific(resourceType, view, processType, factory) {
        var key : string = resourceType + "@" + view + "@" + processType;
        this.specifics[key] = factory;
        return this;
    }
}


/**
 * The resourceArea does not do much by itself. Just like topLevelState, it provides
 * an infrastructure that can be configured in a variety of ways.
 *
 * The general idea is that the path contains a path to a backend resource and
 * optionally a *view* which is preceded by "@". So the path
 *
 *     /adhocracy/proposal/VERSION_0000001/@edit
 *
 * would be mapped to a resource at `<rest_url>/adhocracy/proposal/VERSION_0000001`
 * and view `"edit"`. If no view is provided, it defaults to `""`.
 *
 * Additionally, resources typically belong to a specific *process*. resourceArea
 * automatically finds that process and extracts it `processType`. If a resource is
 * not part of a process, `processType` defaults to `""`.
 *
 * The state `data` object as used by resourceArea consists of three different parts:
 *
 * -   meta
 * -   defaults
 * -   specifics
 *
 * Meta values are used as a communication channel between `route()` and `reverse()`
 * and are generally not of interest outside of resourceArea.
 *
 * Defaults can be configured per contentType/view combination. They can be
 * overwritten in `search`. Any parameters from search that do not exists in defaults
 * are removed. Defaults can be configured like this:
 *
 *     resourceAreaProvider.default("<contentType>", "<view>", "<processType>", {
 *         key: "value",
 *         foo: "bar"
 *     });
 *
 * Specifics are also configured per contentType/view/processType combination. But they
 * are not provided as a plain object. Instead, they are provided in form of a injectable
 * factory that returns a function that takes the actual resource as a parameter and
 * returns the specifics (that may optionally be wrapped in a promise). This sounds
 * complex, but it allows for a great deal of flexibility. Specifics can be configured
 * like this:
 *
 *     resourceAreaProvider.specific("<contentType>", "<view>", "<processType>", ["adhHttp", (adhHttp) => {
 *         return (resource) => {
 *             adhHttp.get(resource.data[<someSheet>.nick].reference).then((referencedResource) => {
 *                 return {
 *                     foo: referencedResource.name
 *                 };
 *             });
 *         };
 *     }]);
 *
 * As meta, defaults and specifics all exist in the same `data` object, name clashes are
 * possible. In those cases, search overwrites specifics overwrites meta overwrites defaults.
 */
export class Service implements AdhTopLevelState.IAreaInput {
    public templateUrl : string;

    constructor(
        private provider : Provider,
        private $q : angular.IQService,
        private $injector : angular.auto.IInjectorService,
        private $location : angular.ILocationService,
        private adhHttp : AdhHttp.Service<any>,
        private adhConfig : AdhConfig.IService,
        private adhResourceUrlFilter
    ) {
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/ResourceArea.html";
    }

    private getDefaults(resourceType : string, view : string, processType : string) : Dict {
        var key : string = resourceType + "@" + view + "@" + processType;
        return <Dict>_.extend({}, this.provider.defaults[key]);
    }

    private getSpecifics(resource, view : string, processType : string) : angular.IPromise<Dict> {
        var key : string = resource.content_type + "@" + view + "@" + processType;
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

    /**
     * Promise the process type of next ancestor process.
     *
     * Promise "" if none could be found.
     *
     * FIXME: don't really know how to do this yet
     */
    private getProcessType(resourceUrl : string) : angular.IPromise<string> {
        return this.$q.when("");
    }

    private conditionallyRedirectVersionToLast(resourceUrl : string) : angular.IPromise<boolean> {
        var self : Service = this;

        return self.adhHttp.get(resourceUrl).then((resource : ResourcesBase.Resource) => {
            if (resource.data.hasOwnProperty(SIVersionable.nick)) {
                if (resource.data[SIVersionable.nick].followed_by.length === 0) {
                    return false;
                } else {
                    var itemUrl = AdhUtil.parentPath(resourceUrl);
                    return self.adhHttp.getNewestVersionPathNoFork(itemUrl).then((lastUrl) => {
                        self.$location.path(self.adhResourceUrlFilter(lastUrl));
                        return true;
                    });

                }
            } else {
                return false;
            }
        });
    }

    public route(path : string, search : Dict) : angular.IPromise<Dict> {
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

        var resourceUrl : string = this.adhConfig.rest_url + segs.join("/") + "/";

        return self.$q.all([
            self.adhHttp.get(resourceUrl),
            self.getProcessType(resourceUrl),
            self.conditionallyRedirectVersionToLast(resourceUrl)
        ]).then((values : any[]) => {
            var resource : ResourcesBase.Resource = values[0];
            var processType : string = values[1];
            var hasRedirected : boolean = values[2];

            if (hasRedirected) {
                return;
            }

            return self.getSpecifics(resource, view, processType).then((specifics : Dict) => {
                var defaults : Dict = self.getDefaults(resource.content_type, view, processType);

                var meta : Dict = {
                    processType: processType,
                    platformUrl: self.adhConfig.rest_url + "/" + segs[1],
                    contentType: resource.content_type,
                    resourceUrl: resourceUrl,
                    view: view
                };

                return _.extend(defaults, meta, specifics, search);
            });
        }, () => {
            throw 404;
        });
    }

    public reverse(data : Dict) : { path : string; search : Dict; } {
        var defaults = this.getDefaults(data["contentType"], data["view"], data["processType"]);
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


export var resourceUrl = (adhConfig : AdhConfig.IService) => {
    return (path : string, view? : string, search? : {[key : string]: any}) => {
        if (typeof path !== "undefined") {
            var url = "/r" + path.replace(adhConfig.rest_url, "");
            if (url.substr(-1) !== "/") {
                url += "/";
            }
            if (typeof view !== "undefined") {
                url += "@" + view;
            }
            if (typeof search !== "undefined") {
                url += "?" + _.map(search, (value, key : string) => {
                    return encodeURIComponent(key) + "=" + encodeURIComponent(value);
                }).join("&");
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
            AdhProcess.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("r", ["adhResourceArea", (adhResourceArea : Service) => adhResourceArea]);
        }])
        .provider("adhResourceArea", Provider)
        .filter("adhResourceUrl", ["adhConfig", resourceUrl]);
};
