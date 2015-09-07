import AdhEmbed = require("../Embed/Embed");

import AdhShareSocial = require("./ShareSocial");


export var moduleName = "adhSocialShare";

export var register = (angular) => {
    return angular
        .module(moduleName, [])
        .config(["$injector", ($injector) => {
            if ($injector.has("adhEmbedProvider")) {
                var adhEmbedProvider : AdhEmbed.Provider = $injector.get("adhEmbedProvider");
                adhEmbedProvider.registerEmbeddableDirectives(["social-share"]);
            }
        }])
        .directive("adhSocialShare", ["adhConfig", "$location", "$document", AdhShareSocial.socialShare]);
};
