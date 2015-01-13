import socialSharePrivacy = require("socialSharePrivacy");  if (socialSharePrivacy) { ; }

import AdhConfig = require("../Config/Config");

export var PATH = "/static/lib/jquery.socialshareprivacy/socialshareprivacy/";


export var socialShare = (adhConfig : AdhConfig.IService, $location : ng.ILocationService, $document : ng.IDocumentService) => {
    return {
        restrict: "E",
        link: (scope, element, attrs) => {
            element.socialSharePrivacy({
                css_path: PATH + "socialshareprivacy.css",
                lang_path: PATH + "lang/",
                language: adhConfig.locale,  // FIXME: does not watch adhConfig.locale
                info_link: "http://www.heise.de/ct/artikel/2-Klicks-fuer-mehr-Datenschutz-1333879.html",
                uri: attrs.uri ? attrs.uri : $location.absUrl(),
                services : {
                    facebook : {
                        perma_option: "off"
                    },
                    twitter : {
                        tweet_text: attrs.tweetText ? attrs.tweetText : document.title,
                        perma_option: "off"
                    },
                    gplus : {
                        perma_option: "off"
                    }
                }
            });

            element.find(".help_info").each(function() {
                var e = $(this);
                var info = e.find(".info");

                e.attr("title", info.text());
                info.remove();
            });
        }
    };
};


export var moduleName = "adhSocialShare";

export var register = (angular) => {
    return angular
        .module(moduleName, [])
        .directive("adhSocialShare", ["adhConfig", "$location", "$document", socialShare]);
};
