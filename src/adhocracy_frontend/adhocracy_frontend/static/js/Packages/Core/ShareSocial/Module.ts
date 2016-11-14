import * as socialSharePrivacy from "socialSharePrivacy";  if (socialSharePrivacy) { ; }

import * as AdhEmbed from "../Embed/Embed";

import * as AdhShareSocial from "./ShareSocial";


export var moduleName = "adhSocialShare";

export var register = (angular) => {
    return angular
        .module(moduleName, [])
        .config(["$injector", ($injector) => {
            if ($injector.has("adhEmbedProvider")) {
                var adhEmbedProvider : AdhEmbed.Provider = $injector.get("adhEmbedProvider");
                adhEmbedProvider.registerDirective("social-share");
            }
        }])
        .directive("adhSocialShare", ["adhConfig", "$location", "$document", AdhShareSocial.socialShare]);
};
