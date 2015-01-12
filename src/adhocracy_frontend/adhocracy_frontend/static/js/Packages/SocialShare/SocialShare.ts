import socialSharePrivacy = require("socialSharePrivacy");  if (socialSharePrivacy) { ; }

import AdhConfig = require("../Config/Config");


export var socialShare = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        link: (scope, element, attrs) => {
            element.socialSharePrivacy({
                path_prefix: "/static/lib/SocialSharePrivacy/build/",
                css_path: "stylesheets/jquery.socialshareprivacy.min.css",
                lang_path: "javascrips/",
                language: adhConfig.locale  // FIXME: does not watch adhConfig.locale
            });
        }
    };
};


export var moduleName = "adhSocialShare";

export var register = (angular) => {
    return angular
        .module(moduleName, [])
        .directive("adhSocialShare", socialShare);
};
