/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhCredentials = require("../User/Credentials");
import AdhHttp = require("../Http/Http");
import AdhEmbed = require("../Embed/Embed");

import SIBadgeable = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeable");
import SIBadgeAssignment = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment");
import SIDescription = require("../../Resources_/adhocracy_core/sheets/description/IDescription");
import RIBadgeAssignment = require("../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");

var pkgLocation = "/Badge";

export interface IBadge {
    title : string;
    description : string;
    name : string;
}

export interface IGetBadges {
    (resource : SIBadgeable.HasSheet) : angular.IPromise<IBadge[]>;
}

export var getBadgesFactory = (
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService
) : IGetBadges => (
    resource : SIBadgeable.HasSheet
) : angular.IPromise<IBadge[]> => {
    var assignmentPaths = resource.data[SIBadgeable.nick].assignments;

    var getBadge = (assignmentPath : string) => {
        return adhHttp.get(assignmentPath).then((assignment : RIBadgeAssignment) => {
            var badgePath = assignment.data[SIBadgeAssignment.nick].badge;
            return adhHttp.get(badgePath).then((badge) => {
                return {
                    title: badge.data[SITitle.nick].title,
                    name: badge.data[SIName.nick].name,
                    description: assignment.data[SIDescription.nick].description
                };
            });
        });
    };

    return $q.all(_.map(assignmentPaths, getBadge));
};

export var badgeAssignmentDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService,
    adhCredentials : AdhCredentials.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Assignment.html",
        scope: {
            badgesPath: "@",
            poolpath: "@",
            badgeablePath: "@"

        },
        link: (scope, element) => {
            scope.data = {
                badge : "",
                description:""
            };

            var getBadgePromise = (badgepath : string) => {
                return adhHttp.get(badgepath);
            };

            var getBadge = (badge) => {
                return {
                    title: badge.data[SITitle.nick].title,
                    path: badge.path
                };
            }

            adhHttp.get(scope.badgesPath).then((badges) => {
                var badgelist = badges["data"]["adhocracy_core.sheets.pool.IPool"]["elements"];
                $q.all(<any>(_.map(badgelist, getBadgePromise))).then((result)=>{
                    scope.badges = _.map(result, getBadge);
                });
            });

            scope.submit = () => {
                var postdata = {
                    content_type: "adhocracy_core.resources.badge.IBadgeAssignment",
                    data: {}
                };
                postdata.data[SIDescription.nick] = {
                    description: scope.data.description
                };
                postdata.data[SIBadgeAssignment.nick] = {
                    badge : scope.data.badge,
                    object : scope.badgeablePath,
                    subject : adhCredentials.userPath
                }
                return adhHttp.post(scope.poolpath, postdata);
            };
        }
    };
};


export var moduleName = "adhBadge";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("assign-badge");
        }])
        .factory("adhGetBadges", ["adhHttp", "$q", getBadgesFactory])
        .directive("adhAssignBadge", ["adhConfig", "adhHttp", "$q", "adhCredentials", badgeAssignmentDirective]);
};
