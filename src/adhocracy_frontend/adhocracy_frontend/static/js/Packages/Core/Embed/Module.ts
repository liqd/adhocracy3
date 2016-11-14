import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

import * as AdhEmbed from "./Embed";


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
        .directive("adhHeader", ["adhEmbed", AdhEmbed.headerDirective])
        .filter("adhCanonicalUrl", ["adhConfig", AdhEmbed.canonicalUrl]);
};
