/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhCredentials = require("../User/Credentials");
import AdhHttp = require("../Http/Http");
import AdhEmbed = require("../Embed/Embed");

import RIBadgeAssignment = require("../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment");
import SIBadgeable = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeable");
import SIBadgeAssignment = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment");
import SIDescription = require("../../Resources_/adhocracy_core/sheets/description/IDescription");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");
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


export var bindPath = (
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService
) => (
    scope,
    pathKey? : string
) : void => {
    scope.data = {
        badge: "",
        description: ""
    };

    var getBadge = (badge) => {
        return {
            title: badge.data[SITitle.nick].title,
            path: badge.path
        };
    };

    adhHttp.get(scope.badgesPath).then((badges) => {
        var badgelist : string[] = badges.data[SIPool.nick].elements;
        $q.all(_.map(badgelist, (b) => adhHttp.get(b))).then((result) => {
            scope.badges = _.map(result, getBadge);
        });
    });

    if (typeof pathKey !== "undefined") {
        scope.$watch(pathKey, (path : string) => {
            if (path) {
                adhHttp.get(path).then((resource) => {
                    scope.resource = resource;
                    scope.badgeablePath = resource.data[SIBadgeAssignment.nick].object;
                    scope.data = {
                        description: resource.data[SIDescription.nick].description,
                        badge: resource.data[SIBadgeAssignment.nick].badge
                    };
                });
            }
        });
    }
};

export var fill = (resource, scope, userPath : string) => {
    var clone = _.cloneDeep(resource);
    clone.data[SIDescription.nick] = {
        description: scope.data.description
    };
    clone.data[SIBadgeAssignment.nick] = {
        badge : scope.data.badge,
        object : scope.badgeablePath,
        subject : userPath
    };
    return clone;
};

export var badgeAssignmentCreateDirective = (
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
            poolPath: "@",
            badgeablePath: "@"
        },
        link: (scope, element) => {
            bindPath(adhHttp, $q)(scope);

            scope.submit = () => {
                var postdata = {
                    content_type: RIBadgeAssignment.content_type,
                    data: {}
                };
                return adhHttp.post(scope.poolPath, fill(postdata, scope, adhCredentials.userPath));
            };
        }
    };
};

export var badgeAssignmentEditDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService,
    adhCredentials : AdhCredentials.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Assignment.html",
        scope: {
            path: "@",
            badgesPath: "@"
        },
        link: (scope, element) => {
            bindPath(adhHttp, $q)(scope, "path");

            scope.submit = () => {
                var resource = scope.resource;
                return adhHttp.put(resource.path, fill(resource, scope, adhCredentials.userPath));
            };
        }
    };
};

export var moduleName = "adhBadge";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentials.moduleName,
            AdhEmbed.moduleName,
            AdhHttp.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("badge-assignment-create");
            adhEmbedProvider.embeddableDirectives.push("badge-assignment-edit");
        }])
        .factory("adhGetBadges", ["adhHttp", "$q", getBadgesFactory])
        .directive("adhBadgeAssignmentCreate", ["adhConfig", "adhHttp", "$q", "adhCredentials", badgeAssignmentCreateDirective])
        .directive("adhBadgeAssignmentEdit", ["adhConfig", "adhHttp", "$q", "adhCredentials", badgeAssignmentEditDirective]);
};
