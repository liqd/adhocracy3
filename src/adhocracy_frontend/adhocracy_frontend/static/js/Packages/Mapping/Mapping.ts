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
            zoom: "@?"
        },
        restrict: "E",
        template: "<div class=\"map\" style=\"cursor:crosshair;\"></div>",
        link: (scope, element, attrs) => {
            var mapElement = element.find(".map");
            mapElement.height(attrs.height);

            var map = leaflet.map(mapElement[0], {
                center: leaflet.latLng(attrs.lat, attrs.lng),
                zoom: attrs.zoom || 14
            });
            leaflet.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);

            var marker = leaflet.marker(leaflet.latLng(scope.lat, scope.lng), {draggable: true});
            adhClickContext(map).on("sglclick", (event : L.LeafletMouseEvent) => {
                marker.setLatLng(event.latlng);
                marker.addTo(map);
                $timeout(() => {
                    scope.lat = event.latlng.lat;
                    scope.lng = event.latlng.lng;
                });
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
            height: "@",
            zoom: "@?"
        },
        restrict: "E",
        template: "<div class=\"map\"></div>",
        link: (scope, element, attrs) => {
            var mapElement = element.find(".map");
            mapElement.height(attrs.height);

            var map = leaflet.map(mapElement[0], {
                center: leaflet.latLng(attrs.lat, attrs.lng),
                zoom: attrs.zoom || 14
            });
            leaflet.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);
            leaflet.marker(leaflet.latLng(scope.lat, scope.lng)).addTo(map);
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
