/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhEmbed = require("../Embed/Embed");


export var mapinput = (adhClickContext, $timeout : angular.ITimeoutService, leaflet : typeof L) => {
    return {
        scope: {
            lat: "=",
            lng: "=",
            height: "@",
            polygon: "=",
            zoom: "@?"
        },
        restrict: "E",
        template: "<div class=\"map\"></div>",
        link: (scope, element, attrs) => {
            var mapElement = element.find(".map");
            mapElement.height(attrs.height);

            var map = leaflet.map(mapElement[0]);
            leaflet.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);
            attrs.polygon.addTo(map);

            // limit map to polygon
            map.fitBounds(attrs.polygon.getBounds());
            leaflet.Util.setOptions(map, {
                minZoom: map.getZoom(),
                maxBounds: map.getBounds()
            });

            if (typeof scope.zoom !== "undefined") {
                map.setZoom(scope.zoom);
            }

            var marker = leaflet.marker(leaflet.latLng(scope.lat, scope.lng), {draggable: true});
            adhClickContext(attrs.polygon).on("sglclick", (event : L.LeafletMouseEvent) => {
                marker.setLatLng(event.latlng);
                marker.addTo(map);
                $timeout(() => {
                    scope.lat = event.latlng.lat;
                    scope.lng = event.latlng.lng;
                });
            });
            attrs.polygon.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });
            map.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });
            marker.on("dragend", (event : L.LeafletDragEndEvent) => {
                var result = event.target.getLatLng();
                $timeout(() => {
                    scope.lat = result.lat;
                    scope.lng = result.lng;
                });
            });
        }
    };
};

export var mapdetail = (leaflet : typeof L) => {
    return {
        scope: {
            lat: "@",
            lng: "@",
            polygon: "@",
            height: "@",
            zoom: "@?"
        },
        restrict: "E",
        template: "<div class=\"map\"></div>",
        link: (scope, element) => {

            var mapElement = element.find(".map");
            mapElement.height(scope.height);

            scope.map = leaflet.map(mapElement[0]);
            leaflet.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(scope.map);
            scope.polygon = leaflet.polygon((<any>leaflet.GeoJSON).coordsToLatLngs(scope.polygon));
            scope.polygon.addTo(scope.map);

            scope.map.fitBounds(scope.polygon.getBounds());
            leaflet.Util.setOptions(scope.map, {
                minZoom: scope.map.getZoom(),
                maxBounds: scope.map.getBounds()
            });
            leaflet.marker(leaflet.latLng(scope.lat, scope.lng)).addTo(scope.map);
        }
    };
};


export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhEmbed.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerEmbeddableDirectives(["map-input", "map-detail"]);
        }])
        .directive("adhMapInput", ["adhClickContext", "$timeout", "leaflet", mapinput])
        .directive("adhMapDetail", ["leaflet", mapdetail]);
};
