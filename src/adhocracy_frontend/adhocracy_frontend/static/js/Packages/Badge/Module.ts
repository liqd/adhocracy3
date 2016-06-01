import * as AdhCredentialsModule from "../User/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhEmbedModule from "../Embed/Module";
import * as AdhMovingColumnsModule from "../MovingColumns/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhEmbed from "../Embed/Embed";

import * as AdhBadge from "./Badge";


export var moduleName = "adhBadge";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider
                .registerDirective("badge-assignment-create")
                .registerDirective("badge-assignment-edit");
        }])
        .factory("adhGetBadges", ["adhHttp", "$q", AdhBadge.getBadgesFactory])
        .directive("adhBadgeAssignment", [
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhPreliminaryNames",
            "$q",
            "adhCredentials",
            "adhGetBadges",
            AdhBadge.badgeAssignment]);
};
