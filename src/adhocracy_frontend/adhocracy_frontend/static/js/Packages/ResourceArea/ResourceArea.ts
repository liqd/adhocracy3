import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

import RIBasicPool = require("../../Resources_/adhocracy_core/resources/pool/IBasicPool");
import RIMercatorProposal = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposal");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");


export class Service implements AdhTopLevelState.IAreaInput {
    public template : string = "<adh-page-wrapper><adh-document-workbench></adh-document-workbench></adh-page-wrapper>";

    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private adhConfig : AdhConfig.IService
    ) {}

    public route(path : string, search : {[key : string]: string}) : ng.IPromise<{[key : string]: string}> {
        var resourceUrl = this.adhConfig.rest_url + path;

        return this.adhHttp.get(resourceUrl).then((resource) => {
            var data = {};

            switch (resource.content_type) {
                case RIBasicPool.content_type:
                    data["space"] = "content";
                    data["movingColumns"] = "is-show-show-hide";
                    break;
                case RIMercatorProposal.content_type:
                    data["space"] = "content";
                    data["movingColumns"] = "is-show-show-hide";
                    break;
                case RIUser.content_type:
                    data["space"] = "user";
                    data["movingColumns"] = "is-show-show-hide";
                    break;
                case RIUsersService.content_type:
                    data["space"] = "user";
                    data["movingColumns"] = "is-show-show-hide";
                    break;
                default:
                    throw "404";
            }
            for (var key in search) {
                if (search.hasOwnProperty(key)) {
                    data[key] = search[key];
                }
            }
            return data;
        });
    }

    public reverse(data : {[key : string]: string}) {
        var defaults = {
            space: "content",
            movingColumns: "is-show-show-hide",
            content2Url: ""
        };

        return {
            path: "/adhocracy",
            search: _.transform(data, (result, value : string, key : string) => {
                if (defaults.hasOwnProperty(key) && value !== defaults[key]) {
                    result[key] = value;
                }
            })
        };
    }
}


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
        .service("adhResourceArea", ["adhHttp", "adhConfig", Service]);
};
