import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhInjectModule = require("../Inject/Module");
import AdhListingModule = require("../Listing/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhWebSocketModule = require("../WebSocket/Module");

import AdhEmbed = require("../Embed/Embed");
import AdhListing = require("../Listing/Listing");

import AdhMapping = require("./Mapping");


export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhInjectModule.moduleName,
            AdhListingModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhWebSocketModule.moduleName,
            "duScroll"
        ])
        .provider("adhMapData", AdhMapping.MapDataProvider)
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerEmbeddableDirectives(["map-input", "map-detail", "map-listing-internal"]);
        }])
        .config(["adhMapDataProvider", (adhMapDataProvider : AdhMapping.MapDataProvider) => {
            adhMapDataProvider.style = {
                fillColor: "#000",
                color: "#000",
                opacity: 0.5,
                stroke: false
            };

            adhMapDataProvider.icons["item"] = {
                className: "icon-map-pin",
                iconAnchor: [17.5, 41],
                iconSize: [35, 42]
            };
            adhMapDataProvider.icons["add"] = {
                className: "icon-map-pin-add",
                iconAnchor: [16.5, 41],
                iconSize: [35, 42]
            };
            adhMapDataProvider.icons["item-selected"] = {
                className: "icon-map-pin is-active",
                iconAnchor: [17.5, 41],
                iconSize: [33, 42]
            };
        }])
        .directive("adhMapInput", ["adhConfig", "adhSingleClickWrapper", "adhMapData", "$timeout", "leaflet", AdhMapping.mapInput])
        .directive("adhMapDetail", ["adhMapData", "leaflet", "$timeout", AdhMapping.mapDetail])
        .directive("adhMapListingInternal", ["adhConfig", "adhHttp", AdhMapping.mapListingInternal])
        .directive("adhMapListing", ["adhConfig", "adhWebSocket", (adhConfig, adhWebSocket) =>
                new AdhMapping.Listing(new AdhListing.ListingPoolAdapter()).createDirective(adhConfig, adhWebSocket)]);
};
