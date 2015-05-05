/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>

import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");

import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhListing = require("../Listing/Listing");
import AdhWebSocket = require("../WebSocket/WebSocket");

// FIXME: See #1008
import AdhHttp = require("../Http/Http");  if (AdhHttp) { ; }
import AdhPermissions = require("../Permissions/Permissions");  if (AdhPermissions) { ; }
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");  if (AdhPreliminaryNames) { ; }

import AdhMappingUtils = require("./MappingUtils");

var pkgLocation = "/Mapping";


export var style = {
    fillColor: "#000",
    color: "#000",
    opacity: 0.5,
    stroke: false
};

export var cssItemIcon = {
    className: "icon-map-pin",
    iconAnchor: [17.5, 41],
    iconSize: [35, 42]
};

export var cssAddIcon = {
    className: "icon-map-pin-add",
    iconAnchor: [16.5, 41],
    iconSize: [35, 42]
};

export var cssSelectedItemIcon = {
    className: "icon-map-pin is-active",
    iconAnchor: [17.5, 41],
    iconSize: [33, 42]
};


var refreshAfterColumnExpandHack = (
    $timeout : angular.ITimeoutService,
    leaflet : typeof L
) => (map : L.Map, bounds : L.LatLngBounds) => {
    $timeout(() => {
        map.invalidateSize(false);
        map.fitBounds(bounds);
        leaflet.Util.setOptions(map, {
            minZoom: map.getZoom()
        });
    }, 500);  // FIXME: moving column transition duration
};

export interface IMapInputScope extends angular.IScope {
    lat : number;
    lng : number;
    height : number;
    polygon : L.Polygon;
    rawPolygon : any;
    zoom? : number;
    text : string;
    error : boolean;
    mapClicked : boolean;
    saveCoordinates() : void;
    resetCoordinates() : void;
}

export var mapInput = (
    adhConfig : AdhConfig.IService,
    adhSingleClickWrapper,
    $timeout : angular.ITimeoutService,
    leaflet : typeof L
) => {
    return {
        scope: {
            lat: "=",
            lng: "=",
            height: "@",
            rawPolygon: "=polygon",
            zoom: "@?"
        },
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Input.html",
        link: (scope : IMapInputScope, element) => {

            var tmpLng : number = _.clone(scope.lng);
            var tmpLat : number = _.clone(scope.lat);

            var mapElement = element.find(".map");
            mapElement.height(scope.height);

            var map = leaflet.map(mapElement[0]);
            leaflet.tileLayer("http://maps.berlinonline.de/tile/bright/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);

            scope.polygon = leaflet.polygon(leaflet.GeoJSON.coordsToLatLngs(scope.rawPolygon), style);
            scope.polygon.addTo(map);

            // limit map to polygon
            map.fitBounds(scope.polygon.getBounds());
            leaflet.Util.setOptions(map, {
                minZoom: map.getZoom()
            });

            if (typeof scope.zoom !== "undefined") {
                map.setZoom(scope.zoom);
            }

            var selectedItemLeafletIcon = (<any>leaflet).divIcon(cssAddIcon);
            var marker : L.Marker;

            var createMarker = (latlng : L.LatLng) : void => {
                marker = leaflet
                    .marker(latlng)
                    .setIcon(selectedItemLeafletIcon)
                    .addTo(map)

                    // only allow to change location by dragging if the new point is inside the polygon
                    .on("dragend", (event : L.LeafletDragEndEvent) => {
                        var result = event.target.getLatLng();
                        var pointInPolygon = AdhMappingUtils.pointInPolygon(result, scope.polygon);

                        if (pointInPolygon) {
                            scope.mapClicked = true;
                            $timeout(() => {
                                tmpLat = result.lat;
                                tmpLng = result.lng;
                            });
                        } else {
                            marker.setLatLng(leaflet.latLng(tmpLat, tmpLng));
                            marker.dragging.disable();
                            $timeout(() => {
                                scope.text = "TR__MAP_MARKER_ERROR";
                                scope.error = true;
                                $timeout(() => {
                                    scope.text = "TR__MAP_EXPLAIN_DRAG";
                                    marker.dragging.enable();
                                    scope.error = false;
                                }, 2000);
                            });
                        }
                    });
            };

            if (typeof scope.lat !== "undefined" && typeof scope.lng !== "undefined") {
                createMarker(leaflet.latLng(scope.lat, scope.lng));
                marker.dragging.enable();

                scope.text = "TR__MAP_EXPLAIN_DRAG";
            } else {
                scope.text = "TR__MAP_EXPLAIN_CLICK";
            }

            // when the polygon is clicked, set the marker there
            adhSingleClickWrapper(scope.polygon).on("sglclick", (event : L.LeafletMouseEvent) => {
                if (typeof marker === "undefined") {
                    createMarker(event.latlng);
                } else {
                    marker.setLatLng(event.latlng);
                }
                marker.dragging.enable();
                $timeout(() => {
                    tmpLat = event.latlng.lat;
                    tmpLng = event.latlng.lng;
                    scope.text = "TR__MAP_EXPLAIN_DRAG";
                    scope.mapClicked = true;
                });
            });

            scope.polygon.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });
            map.on("dblclick", (event : L.LeafletMouseEvent) => {
                map.zoomIn();
            });

            scope.saveCoordinates = () => {
                scope.lng = tmpLng;
                scope.lat = tmpLat;
                scope.mapClicked = false;
                scope.text = "TR__MAP_MARKER_SAVED";
                $timeout(() => {
                    scope.text = "TR__MAP_EXPLAIN_DRAG";
                }, 2000);
            };

            scope.resetCoordinates = () => {
                tmpLng = undefined;
                tmpLat = undefined;
                scope.lng = undefined;
                scope.lat = undefined;
                map.removeLayer(marker);
                marker = undefined;
                scope.mapClicked = false;
                scope.text = "TR__MAP_EXPLAIN_CLICK";
            };

            refreshAfterColumnExpandHack($timeout, leaflet)(map, scope.polygon.getBounds());
        }
    };
};

export var mapDetail = (leaflet : typeof L, $timeout : angular.ITimeoutService) => {
    return {
        scope: {
            lat: "=",
            lng: "=",
            polygon: "=",
            height: "@",
            zoom: "@?"
        },
        restrict: "E",
        template: "<div class=\"map\"></div>",
        link: (scope, element) => {

            var mapElement = element.find(".map");
            mapElement.height(scope.height);

            scope.map = leaflet.map(mapElement[0]);
            leaflet.tileLayer("http://maps.berlinonline.de/tile/bright/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(scope.map);
            scope.polygon = leaflet.polygon(leaflet.GeoJSON.coordsToLatLngs(scope.polygon), style);
            scope.polygon.addTo(scope.map);

            scope.map.fitBounds(scope.polygon.getBounds());
            leaflet.Util.setOptions(scope.map, {
                minZoom: scope.map.getZoom()
            });

            scope.marker = leaflet
                .marker(leaflet.latLng(scope.lat, scope.lng))
                .setIcon((<any>leaflet).divIcon(cssSelectedItemIcon))
                .addTo(scope.map);

            scope.$watchGroup(["lat", "lng"], (newValues) => {
                scope.marker.setLatLng(leaflet.latLng(newValues[0], newValues[1]));
            });

            refreshAfterColumnExpandHack($timeout, leaflet)(scope.map, scope.polygon.getBounds());
        }

    };
};


export interface IMapListScope extends angular.IScope {
    height : number;
    polygon : L.Polygon;
    rawPolygon : number[][];
    items : string[];
    selectedPath : string;
    selectItem(path : string) : void;
    getPreviousItem() : void;
    getNextItem() : void;
    showZoomButton : boolean;
    resetMap() : void;
    visibleItems : number;
}

export class MapListingController {
    private map : L.Map;
    private scrollContainer;
    private selectedItemLeafletIcon;
    private itemLeafletIcon;
    private markers : {[path : string]: L.Marker};

    constructor(
        private $scope : IMapListScope,
        private $element,
        private $attrs,
        private $timeout : angular.ITimeoutService,
        private leaflet : typeof L
    ) {
        this.scrollContainer = this.$element.find(".map-list-scroll-container-inner");
        this.selectedItemLeafletIcon = (<any>leaflet).divIcon(cssSelectedItemIcon);
        this.itemLeafletIcon = (<any>leaflet).divIcon(cssItemIcon);
        this.markers = {};

        this.map = this.createMap();

        this.$scope.visibleItems = 0;

        this.$scope.selectItem = (path : string) => {
            if (this.isVisible(path)) {
                if (this.markers.hasOwnProperty(this.$scope.selectedPath)) {
                    this.markers[this.$scope.selectedPath].setIcon(this.itemLeafletIcon);
                }
                this.$scope.selectedPath = path;
                this.markers[this.$scope.selectedPath].setIcon(this.selectedItemLeafletIcon);
                this.scrollToItem(path);
            }
        };

        this.$scope.getPreviousItem = () => {
            this.getRelativeItem(-1);
        };

        this.$scope.getNextItem = () => {
            this.getRelativeItem(1);
        };

        this.$scope.resetMap = () => {
            this.map.invalidateSize(false);
            this.map.fitBounds(this.$scope.polygon.getBounds());

            // this is hacky but I could not find how to add
            // a callback function to fitbounds as this always
            // triggers the moveend event.
            this.$timeout(() => {
                this.$scope.showZoomButton = false;
            }, 300);
        };
    }

    private createMap() {
        var mapElement = this.$element.find(".map-list-map");
        mapElement.height(this.$scope.height);

        var map = this.leaflet.map(mapElement[0]);
        this.leaflet.tileLayer("http://maps.berlinonline.de/tile/bright/{z}/{x}/{y}.png", {maxZoom: 18}).addTo(map);

        this.$scope.polygon = this.leaflet.polygon(this.leaflet.GeoJSON.coordsToLatLngs(this.$scope.rawPolygon), style);
        this.$scope.polygon.addTo(map);

        // limit map to polygon
        map.fitBounds(this.$scope.polygon.getBounds());
        this.leaflet.Util.setOptions(map, {
             minZoom: map.getZoom()
        });

        map.on("moveend", () => {
            this.$scope.visibleItems = 0;
            this.$timeout(() => {
                _.forEach(this.$scope.items, (path) => {
                    if (this.isVisible(path)) {
                        this.$scope.visibleItems++;
                    }
                });
            });
            this.$scope.showZoomButton = true;
        });

        return map;
    }

    private getRelativeItem(offset : number) : void {
        var mod = (index, total) => (index + total) % total;

        var initialIndex = this.pathToIndex(this.$scope.selectedPath);
        var total = this.$scope.items.length;

        var index = mod(initialIndex + offset, total);
        var counter = 0;
        while (!this.isVisible(this.indexToPath(index))) {
            if (counter > total) {
                console.log("Potential infinite loop!");
                return;
            }
            index = mod(index + offset, total);
            counter++;
        }

        this.$scope.selectItem(this.indexToPath(index));
    }

    private scrollToItem(path : string, animate = true) : void {
        // FIXME: this needs to be retriggered when the widget
        // is resized or the index of an item changes.

        var index = this.pathToIndex(path);
        var width = this.$element.find(".map-list-item").width();

        if (this.$attrs.orientation === "vertical") {
            var element = this.$element.find(".map-list-item").eq(index);
            (<any>this.scrollContainer).scrollToElement(element, 10, animate ? 300 : 0);
        } else {
            var left = width * (index + 1);
            (<any>this.scrollContainer).scrollTo(left, 0, animate ? 800 : 0);
        }
    }

    private isVisible(path : string) : boolean {
        if (this.markers.hasOwnProperty(path)) {
            var mapBounds = this.map.getBounds();
            var markerLatLng = this.markers[path].getLatLng();
            return mapBounds.contains(markerLatLng);
        } else {
            return false;
        }
    }

    private pathToIndex(path : string) : number {
        return this.$scope.items.indexOf(path);
    }

    private indexToPath(index : number) : string {
        return this.$scope.items[index];
    }

    private isUndefinedLatLng(lat : number, lng : number) : boolean {
        return lat === 0 && lng === 0;
    }

    public registerListItem(path : string, lat : number, lng : number) : () => void {
        if (this.isUndefinedLatLng(lat, lng)) {
            return () => undefined;
        } else {
            var marker = this.leaflet.marker(this.leaflet.latLng(lat, lng), {
                icon: this.itemLeafletIcon
            });
            marker.addTo(this.map);
            marker.on("click", () => {
                this.$timeout(() => {
                    this.$scope.selectItem(path);
                });
            });
            this.markers[path] = marker;

            if (this.isVisible(path)) {
                this.$scope.visibleItems++;
            }

            return () => {
                if (this.isVisible(path)) {
                    this.$scope.visibleItems--;
                }
                delete this.markers[path];
                this.map.removeLayer(marker);
            };
        }
    }
}

export var mapListingInternal = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        scope: {
            height: "@",
            rawPolygon: "=polygon",
            items: "=",
            emptyText: "@"
        },
        restrict: "E",
        transclude: true,
        templateUrl: (element, attrs) => {
            if (attrs.orientation === "vertical") {
                return adhConfig.pkg_path + pkgLocation + "/ListingInternal.html";
            } else {
                return adhConfig.pkg_path + pkgLocation + "/ListingInternalHorizontal.html";
            }
        },
        controller: ["$scope", "$element", "$attrs", "$timeout", "leaflet", MapListingController]
    };
};


export class Listing<Container extends ResourcesBase.Resource> extends AdhListing.Listing<Container> {
    public static templateUrl : string = pkgLocation + "/Listing.html";

    public createDirective(adhConfig : AdhConfig.IService, adhWebSocket: AdhWebSocket.Service) {
        var directive = super.createDirective(adhConfig, adhWebSocket);
        directive.scope["polygon"] = "=";

        var originalLink = directive.link;
        directive.link = (scope) => {
            originalLink.apply(undefined, arguments);

            // FIXME: only here for manual testing
            scope.changeData = () => {
                scope.elements.splice(0, 1);
            };
        };

        return directive;
    }
}


export var moduleName = "adhMapping";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhEmbed.moduleName,
            AdhListing.moduleName,
            "adhInject",
            "duScroll"
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerEmbeddableDirectives(["map-input", "map-detail", "map-listing-internal"]);
        }])
        .directive("adhMapInput", ["adhConfig", "adhSingleClickWrapper", "$timeout", "leaflet", mapInput])
        .directive("adhMapDetail", ["leaflet", "$timeout", mapDetail])
        .directive("adhMapListingInternal", ["adhConfig", "adhHttp", mapListingInternal])
        .directive("adhMapListing", ["adhConfig", "adhWebSocket", (adhConfig, adhWebSocket) =>
                new Listing(new AdhListing.ListingPoolAdapter()).createDirective(adhConfig, adhWebSocket)]);
};
