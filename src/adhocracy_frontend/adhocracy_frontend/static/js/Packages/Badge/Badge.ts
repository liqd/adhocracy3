/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import _ = require("lodash");

import AdhHttp = require("../Http/Http");

import SIBadgeable = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeable");
import SIBadgeAssignment = require("../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment");
import SIDescription = require("../../Resources_/adhocracy_core/sheets/description/IDescription");
import RIBadgeAssignment = require("../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");


export interface IBadge {
    title : string;
    description : string;
    name : string;
}

export var getBadgesFactory = (
    adhHttp : AdhHttp.Service<any>,
    $q : angular.IQService
) => (resource : SIBadgeable.HasSheet) : angular.IPromise<IBadge[]> => {
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


export var moduleName = "adhBadge";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName
        ])
        .factory("adhGetBadges", ["adhHttp", "$q", getBadgesFactory]);
};
