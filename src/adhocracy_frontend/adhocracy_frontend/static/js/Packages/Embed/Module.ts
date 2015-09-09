import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhTopLevelState = require("../TopLevelState/TopLevelState");

import AdhEmbed = require("./Embed");


export var moduleName = "adhEmbed";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "pascalprecht.translate",
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("embed", ["$location", "adhEmbed", (
                    $location : angular.ILocationService,
                    adhEmbed : AdhEmbed.Service
                ) : AdhTopLevelState.IAreaInput => {
                    return adhEmbed.route($location);
                }]);
        }])
        .run(["$location", "$translate", "adhConfig", ($location, $translate, adhConfig) => {
            // Note: This works despite the routing removing the locale search
            // parameter immediately after. This is a bit awkward though.

            // FIXME: centralize locale setup in adhLocale
            var params = $location.search();
            if (params.hasOwnProperty("locale")) {
                $translate.use(params.locale);
            }
            if (typeof params.locale !== "undefined") {
                adhConfig.locale = params.locale;
            }
        }])
        .provider("adhEmbed", AdhEmbed.Provider)
        .directive("href", ["adhConfig", "$location", "$rootScope", AdhEmbed.hrefDirective])
        .filter("adhCanonicalUrl", ["adhConfig", AdhEmbed.canonicalUrl]);
};
