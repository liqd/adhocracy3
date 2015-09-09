import AdhCredentialsModule = require("../User/Module");
import AdhHttpModule = require("../Http/Module");
import AdhEmbedModule = require("../Embed/Module");

import AdhEmbed = require("../Embed/Embed");

import AdhBadge = require("./Badge");


export var moduleName = "adhBadge";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("badge-assignment-create");
            adhEmbedProvider.embeddableDirectives.push("badge-assignment-edit");
        }])
        .factory("adhGetBadges", ["adhHttp", "$q", AdhBadge.getBadgesFactory])
        .directive("adhBadgeAssignmentCreate", ["adhConfig", "adhHttp", "$q", "adhCredentials", AdhBadge.badgeAssignmentCreateDirective])
        .directive("adhBadgeAssignmentEdit", ["adhConfig", "adhHttp", "$q", "adhCredentials", AdhBadge.badgeAssignmentEditDirective]);
};
