/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhEmbed = require("../Embed/Embed");
import AdhMappingUtils = require("./MappingUtils");
import _ = require("lodash");

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
        template: "<div class=\"ng-class: {myErrorClass: error}\" style=\"padding: 5px; background-color: #FFCCFF; \">" +
                   "{{ text | translate }}" +
                   "</div>" +
                    "<div class=\"map\"></div>" +
                    "<div ng-if=\" mapclicked\" style=\"padding: 5px; background-color: #FFCCFF; \">" +
                        "<div>" +
                            "<a href=\"#\" class=\"button form-footer-button\"" +
                                "data-ng-click=\"saveCoordinates();\" style=\"" +
                                "margin-right: 5px;\" >Speichern</a>" +
                            "<a href=\"#\" class=\"button form-footer-button\"" +
                            "data-ng-click=\"resetCoordinates();\" >Löschen</a>" +
                        "</div>" +
                    "</div>" ,

        link: (scope, element) => {

            scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_CLICK";
            scope.copy_lng = _.clone(scope.lng);
            scope.copy_lat = _.clone(scope.lat);

            var mapElement = element.find(".map");
            mapElement.height(scope.height);

            var map = leaflet.map(mapElement[0]);
            leaflet.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);

            // FIXME: Definetely Typed
            scope.polygon_origin = _.clone(scope.polygon);
            scope.polygon = leaflet.polygon((<any>leaflet.GeoJSON).coordsToLatLngs(scope.polygon));
            scope.polygon.addTo(map);

            // limit map to polygon
            map.fitBounds(scope.polygon.getBounds());
            leaflet.Util.setOptions(map, {
                minZoom: map.getZoom(),
                maxBounds: map.getBounds()
            });

            if (typeof scope.zoom !== "undefined") {
                map.setZoom(scope.zoom);
            }

            scope.marker = (<any>leaflet).marker();


            if (scope.copy_lat && scope.copy_lng) {
                scope.marker.setLatLng(leaflet.latLng(scope.copy_lat, scope.copy_lng)).addTo(map);
                scope.marker.dragging.enable();
                scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
            }

            adhClickContext(scope.polygon).on("sglclick", (event : L.LeafletMouseEvent) => {
                scope.marker.setLatLng(event.latlng);
                scope.marker.addTo(map);
                scope.marker.dragging.enable();
                $timeout(() => {
                    scope.copy_lat = event.latlng.lat;
                    scope.copy_lng = event.latlng.lng;
                    scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                    scope.mapclicked = true;
                });
            });

            scope.polygon.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });
            map.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });

            scope.marker.on("dragend", (event : L.LeafletDragEndEvent) => {

                var result = event.target.getLatLng();
                var pointInPolygon = (AdhMappingUtils.pointInPolygon([result.lat, result.lng], scope.polygon_origin));

                if (pointInPolygon) {
                    scope.mapclicked = true;
                    $timeout(() => {
                        scope.copy_lat = result.lat;
                        scope.copy_lng = result.lng;
                    });
                } else {
                    scope.marker.setLatLng(leaflet.latLng(scope.copy_lat, scope.copy_lng));
                    scope.marker.dragging.disable();
                    $timeout(() => {
                        scope.text = "TR__MEINBERLIN_MAP_MARKER_ERROR";
                        scope.error = true;
                        $timeout(() => {
                            scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                            scope.marker.dragging.enable();
                            scope.error = false;
                        }, 2000);
                    });
                }
            });

            scope.saveCoordinates = () => {
                scope.lng = scope.copy_lng;
                scope.lat = scope.copy_lat;
                scope.mapclicked = false;
                scope.text = "TR__MEINBERLIN_MAP_MARKER_SAVED";
                $timeout(() => {
                    scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                }, 2000);
            };

            scope.resetCoordinates = () => {
                scope.copy_lng = "";
                scope.copy_lat = "";
                scope.lng = "";
                scope.lat = "";
                map.removeLayer(scope.marker);
                scope.mapclicked = false;
                scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_CLICK";
            };
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
        link: (scope, element) => {
            var mapElement = element.find(".map");
            mapElement.height(scope.height);

            var map = leaflet.map(mapElement[0], {
                center: leaflet.latLng(scope.lat, scope.lng),
                zoom: scope.zoom || 14
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
