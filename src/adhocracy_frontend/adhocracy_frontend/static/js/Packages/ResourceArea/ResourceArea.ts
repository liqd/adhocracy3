import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export interface Dict {
    [key : string]: string;
}


export class Provider implements ng.IServiceProvider {
    public $get;
    private data : {[resourceType : string]: Dict};

    constructor() {
        var self = this;
        this.data = {};
        this.$get = ["adhHttp", "adhConfig", (adhHttp, adhConfig) => new Service(self, adhHttp, adhConfig)];
    }

    public when(resourceType : string, defaults : Dict) : Provider {
        this.data[resourceType] = defaults;
        return this;
    }

    public get(resourceType : string) : Dict {
        return _.clone(this.data[resourceType]);
    }
}


export class Service implements AdhTopLevelState.IAreaInput {
    public template : string = "<adh-page-wrapper><adh-platform></adh-platform></adh-page-wrapper>";

    constructor(
        private provider : Provider,
        private adhHttp : AdhHttp.Service<any>,
        private adhConfig : AdhConfig.IService
    ) {}

    public route(path : string, search : Dict) : ng.IPromise<Dict> {
        var self : Service = this;
        var resourceUrl = this.adhConfig.rest_url + path;

        return this.adhHttp.get(resourceUrl).then((resource) => {
            var data = self.provider.get(resource.content_type);
            data["platform"] = path.split("/")[1];

            for (var key in search) {
                if (search.hasOwnProperty(key)) {
                    data[key] = search[key];
                }
            }
            return data;
        });
    }

    public reverse(data : Dict) {
        var defaults = {
            space: "content",
            movingColumns: "is-show-show-hide",
            content2Url: ""
        };

        return {
            path: "/" + data["platform"],
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
        .provider("adhResourceArea", Provider);
};
