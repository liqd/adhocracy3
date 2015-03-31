/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>

import _ = require("lodash");

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhMappingUtils = require("./MappingUtils");

var pkgLocation = "/Mapping";


export interface IMapInputScope extends angular.IScope {
    lat : number;
    lng : number;
    height : number;
    polygon : any;
    zoom? : number;
    text : string;
    error : boolean;
    mapClicked : boolean;
    saveCoordinates() : void;
    resetCoordinates() : void;
    polygon_origin : any;
}

export var mapInput = (adhConfig : AdhConfig.IService, adhClickContext, $timeout : angular.ITimeoutService, leaflet : typeof L) => {
    return {
        scope: {
            lat: "=",
            lng: "=",
            height: "@",
            polygon: "=",
            zoom: "@?"
        },
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Input.html",
        link: (scope : IMapInputScope, element) => {

            var copyLng : number = _.clone(scope.lng);
            var copyLat : number = _.clone(scope.lat);

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

            // FIXME: Definetely Typed
            var marker = (<any>leaflet).marker();

            // check if the geoloation is already set (means we are editing) or not (means we are creating)
            // if yes, show show marker and dragging explanation
            // if no dont show marker and mapclicking explanation
            if (typeof copyLat === "undefined" && typeof copyLng === "undefined") {
                marker.setLatLng(leaflet.latLng(copyLat, copyLng)).addTo(map);
                marker.dragging.enable();
                scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
            } else {
                scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_CLICK";
            }

            // when the polygon is clicked, set the marker there
            // sglclick checks if doubleclick needs to be fired (and zoom in)
            adhClickContext(scope.polygon).on("sglclick", (event : L.LeafletMouseEvent) => {
                marker.setLatLng(event.latlng);
                marker.addTo(map);
                marker.dragging.enable();
                $timeout(() => {
                    copyLat = event.latlng.lat;
                    copyLng = event.latlng.lng;
                    scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                    scope.mapClicked = true;
                });
            });

            scope.polygon.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });
            map.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });

            // only allow to change location by dragging if the new point is inside the polygon
            marker.on("dragend", (event : L.LeafletDragEndEvent) => {
                var result = event.target.getLatLng();
                var pointInPolygon = AdhMappingUtils.pointInPolygon([result.lat, result.lng], scope.polygon_origin);

                if (pointInPolygon) {
                    scope.mapClicked = true;
                    $timeout(() => {
                        copyLat = result.lat;
                        copyLng = result.lng;
                    });
                } else {
                    marker.setLatLng(leaflet.latLng(copyLat, copyLng));
                    marker.dragging.disable();
                    $timeout(() => {
                        scope.text = "TR__MEINBERLIN_MAP_MARKER_ERROR";
                        scope.error = true;
                        $timeout(() => {
                            scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                            marker.dragging.enable();
                            scope.error = false;
                        }, 2000);
                    });
                }
            });

            scope.saveCoordinates = () => {
                scope.lng = copyLng;
                scope.lat = copyLat;
                scope.mapClicked = false;
                scope.text = "TR__MEINBERLIN_MAP_MARKER_SAVED";
                $timeout(() => {
                    scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_DRAG";
                }, 2000);
            };

            scope.resetCoordinates = () => {
                copyLng = undefined;
                copyLat = undefined;
                scope.lng = undefined;
                scope.lat = undefined;
                map.removeLayer(marker);
                scope.mapClicked = false;
                scope.text = "TR__MEINBERLIN_MAP_EXPLAIN_CLICK";
            };
        }
    };
};

export var mapDetail = (leaflet : typeof L) => {
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
        .directive("adhMapInput", ["adhConfig", "adhClickContext", "$timeout", "leaflet", mapInput])
        .directive("adhMapDetail", ["leaflet", mapDetail]);
};
