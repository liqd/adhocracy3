/// <reference path="../../../lib2/types/angular.d.ts"/>
/// <reference path="../../../lib2/types/lodash.d.ts"/>

import * as _ from "lodash";

import * as AdhConfig from "../Config/Config";
import * as AdhCredentials from "../User/Credentials";
import * as AdhHttp from "../Http/Http";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhMovingColumns from "../MovingColumns/MovingColumns";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUtil from "../Util/Util";

import RIBadgeAssignment from "../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment";
import * as SIBadge from "../../Resources_/adhocracy_core/sheets/badge/IBadge";
import * as SIBadgeable from "../../Resources_/adhocracy_core/sheets/badge/IBadgeable";
import * as SIBadgeAssignment from "../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment";
import * as SIDescription from "../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SIName from "../../Resources_/adhocracy_core/sheets/name/IName";
import * as SITitle from "../../Resources_/adhocracy_core/sheets/title/ITitle";

var pkgLocation = "/Badge";

export interface IBadge {
    title : string;
    description : string;
    name : string;
    path : string;
}

export interface IGetBadges {
    (resource : SIBadgeable.HasSheet) : angular.IPromise<IBadge[]>;
}

export var getBadgesFactory = (
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService
) : IGetBadges => (
    resource : SIBadgeable.HasSheet,
    includeParent? : boolean
) : angular.IPromise<IBadge[]> => {
    if (typeof includeParent === "undefined") {
        includeParent = !!resource.content_type.match(/Version$/);
    }

    var assignmentPaths = resource.data[SIBadgeable.nick].assignments;

    var getBadge = (assignmentPath : string) => {
        return adhHttp.get(assignmentPath).then((assignment : RIBadgeAssignment) => {
            var badgePath = assignment.data[SIBadgeAssignment.nick].badge;
            return adhHttp.get(badgePath).then((badge) => {
                return {
                    title: badge.data[SITitle.nick].title,
                    name: badge.data[SIName.nick].name,
                    description: assignment.data[SIDescription.nick].description,
                    path: assignmentPath
                };
            });
        });
    };

    if (includeParent) {
        var parentPath = AdhUtil.parentPath(resource.path);

        return adhHttp.get(parentPath).then((parentResource) => {
            var parentAssignments = parentResource.data[SIBadgeable.nick].assignments;
            assignmentPaths = assignmentPaths.concat(parentAssignments);
            return $q.all(_.map(assignmentPaths, getBadge));
        });
    } else {
        return $q.all(_.map(assignmentPaths, getBadge));
    }
};


export var bindPath = (
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
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
            path: badge.path,
            groups: badge.data[SIBadge.nick].groups
        };
    };

    var getGroup = (group) => {
        return {
            title: group.data[SITitle.nick].title,
            path: group.path
        };
    };

    adhPermissions.bindScope(scope, scope.poolPath, "rawOptions", {importOptions: false});
    scope.$watch("rawOptions", (rawOptions) => {
        var requestBodyOptions = AdhUtil.deepPluck(rawOptions, [
            "data", "POST", "request_body"
        ]);

        var badgeBodyOptions = _.find(
            requestBodyOptions,
            (body : any) => body.content_type === RIBadgeAssignment.content_type);

        var assignableBatchPaths : string = AdhUtil.deepPluck(badgeBodyOptions, [
            "data", SIBadgeAssignment.nick, "badge"
        ]);

        var promise = $q.all(_.map(assignableBatchPaths, (b) => adhHttp.get(b))).then((result) => {
            scope.badges = _.map(result, getBadge);
            return scope.badges;
        });

        promise.then((badges) => {
            var groupPaths = _.union.apply(_, _.map(badges, (badge : any) => badge.groups));

            $q.all(_.map(groupPaths, (g :  any) => adhHttp.get(g))).then((result) => {
                 scope.badgeGroups = _.map(result, getGroup);
            });
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
        badge: scope.data.badge,
        object: scope.badgeablePath,
        subject: userPath
    };
    return clone;
};

export var badgeAssignmentCreateDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions: AdhPermissions.Service,
    $q : angular.IQService,
    adhCredentials : AdhCredentials.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Assignment.html",
        scope: {
            badgeablePath: "@",
            poolPath: "@",
            showDescription: "=?",
            onSubmit: "=?",
            onCancel: "=?"
        },
        link: (scope, element) => {
            bindPath(adhHttp, adhPermissions, $q)(scope);

            scope.submit = () => {
                var postdata = {
                    content_type: RIBadgeAssignment.content_type,
                    data: {}
                };
                return adhHttp.post(scope.poolPath, fill(postdata, scope, adhCredentials.userPath))
                    .then((response) => {
                        scope.serverError = null;
                        if (scope.onSubmit) {
                            scope.onSubmit();
                        }
                    }, (response) => {
                        scope.serverError = response[0].description;
                    });
            };

            scope.cancel = () => {
                if (scope.onCancel) {
                    scope.onCancel();
                }
            };
        }
    };
};

export var badgeAssignmentEditDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions: AdhPermissions.Service,
    $q : angular.IQService,
    adhCredentials : AdhCredentials.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Assignment.html",
        scope: {
            path: "@",
            poolPath: "@",
            showDescription: "=?",
            onSubmit: "=?",
            onCancel: "=?"
        },
        link: (scope, element) => {
            bindPath(adhHttp, adhPermissions, $q)(scope, "path");

            scope.delete = () => {
                return adhHttp.delete(scope.path, RIBadgeAssignment.content_type)
                    .then(() => {
                        scope.serverError = null;
                        if (scope.onSubmit) {
                            scope.onSubmit();
                        }
                    }, (response) => {
                        scope.serverError = response[0].description;
                    });
            };

            scope.submit = () => {
                var resource = scope.resource;
                return adhHttp.put(resource.path, fill(resource, scope, adhCredentials.userPath))
                    .then((response) => {
                        scope.serverError = null;
                        if (scope.onSubmit) {
                            scope.onSubmit();
                        }
                    }, (response) => {
                        scope.serverError = response[0].description;
                    });
            };

            scope.cancel = () => {
                if (scope.onCancel) {
                    scope.onCancel();
                }
            };
        }
    };
};

export var badgeAssignmentDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService,
    adhTopLevelState : AdhTopLevelState.Service,
    adhGetBadges
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Wrapper.html",
        require: "^adhMovingColumn",
        scope: {
            path: "@",
            showDescription: "=?",
            onSubmit: "=?",
            onCancel: "=?"
        },
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.badgeablePath = scope.path;
            scope.data = {};

            adhHttp.get(scope.path).then((proposal) => {
                scope.poolPath = proposal.data[SIBadgeable.nick].post_pool;

                return adhGetBadges(proposal).then((assignments : IBadge[]) => {
                    scope.assignments = assignments;
                });
            });

            scope.submit = () => {
                column.hideOverlay("badges");
                column.alert("TR__BADGE_ASSIGNMENT_UPDATED", "success");
                if (scope.onSubmit) {
                    scope.onSubmit();
                }
            };

            scope.cancel = () => {
                column.hideOverlay("badges");
                if (scope.onCancel) {
                    scope.onCancel();
                }
            };
        }
    };
};
