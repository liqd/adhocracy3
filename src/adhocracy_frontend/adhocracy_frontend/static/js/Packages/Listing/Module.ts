import AdhHttpModule = require("../Http/Module");
import AdhInjectModule = require("../Inject/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhWebSocketModule = require("../WebSocket/Module");

import AdhListing = require("./Listing");


export var moduleName = "adhListing";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhInjectModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhWebSocketModule.moduleName
        ])
        .directive("adhFacets", ["adhConfig", AdhListing.facets])
        .directive("adhListing",
            ["adhConfig", "adhWebSocket", (adhConfig, adhWebSocket) =>
                new AdhListing.Listing(new AdhListing.ListingPoolAdapter()).createDirective(adhConfig, adhWebSocket)]);
};
