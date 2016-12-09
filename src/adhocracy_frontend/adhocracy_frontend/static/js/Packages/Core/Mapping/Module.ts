import * as AdhAngularHelpersModule from "../AngularHelpers/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhInjectModule from "../Inject/Module";
import * as AdhListingModule from "../Listing/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhPreliminaryNamesModule from "../PreliminaryNames/Module";
import * as AdhWebSocketModule from "../WebSocket/Module";

import * as AdhMapping from "./Mapping";


export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhHttpModule.moduleName,
            AdhInjectModule.moduleName,
            AdhListingModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhWebSocketModule.moduleName,
            "duScroll"
        ])
        .provider("adhMapData", AdhMapping.MapDataProvider)
        .config(["adhMapDataProvider", (adhMapDataProvider : AdhMapping.MapDataProvider) => {
            adhMapDataProvider.style = {
                fillColor: "#000",
                color: "#000",
                opacity: 0.5,
                stroke: false
            };

            adhMapDataProvider.icons["item"] = {
                className: "",
                iconSize: [20, 20]
            };
            adhMapDataProvider.icons["add"] = {
                className: "",
                iconSize: [20, 20]
            };
            adhMapDataProvider.icons["item-selected"] = {
                className: "is-active",
                iconSize: [20, 20]
            };
        }])
        .directive("adhMapInput", ["adhConfig", "adhSingleClickWrapper", "adhMapData", "$timeout", "leaflet", AdhMapping.mapInput])
        .directive("adhMapDetail", ["adhConfig", "adhMapData", "leaflet", "$timeout", AdhMapping.mapDetail])
        .directive("adhMapListingInternal", ["adhConfig", "adhHttp", AdhMapping.mapListingInternal])
        .directive("adhMapSwitch", ["adhConfig", AdhMapping.mapSwitch])
        .directive("adhMapListing", ["adhConfig", "adhWebSocket", (adhConfig, adhWebSocket) =>
                new AdhMapping.Listing().createDirective(adhConfig, adhWebSocket)]);
};
