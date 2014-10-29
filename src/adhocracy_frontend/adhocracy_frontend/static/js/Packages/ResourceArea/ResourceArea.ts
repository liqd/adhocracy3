import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");

import RIBasicPool = require("../../Resources_/adhocracy_core/resources/pool/IBasicPool");
import RIMercatorProposal = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposal");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import RIUsersService = require("../../Resources_/adhocracy_core/resources/principal/IUsersService");


export var resourceArea = (
    adhHttp : AdhHttp.Service<any>,
    adhConfig : AdhConfig.IService
) => {
    return {
        template: "<adh-page-wrapper><adh-document-workbench></adh-document-workbench></adh-page-wrapper>",
        route: (path, search) : ng.IPromise<{[key : string]: string}> => {
            var resourceUrl = adhConfig.rest_url + path;

            return adhHttp.get(resourceUrl).then((resource) => {
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
        },
        reverse: (data) => {
            var defaults = {
                space: "content",
                movingColumns: "is-show-show-hide",
                content2Url: ""
            };

            return {
                path: "/adhocracy",
                search: _.transform(data, (result, value, key) => {
                    if (defaults.hasOwnProperty(key) && value !== defaults[key]) {
                        result[key] = value;
                    }
                })
            };
        }
    };
};


export var moduleName = "adhResourceArea";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName
        ]);
};
