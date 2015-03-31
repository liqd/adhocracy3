/// <reference path="../../../lib/DefinitelyTyped/leaflet/leaflet.d.ts"/>

// code comes from https://github.com/substack/point-in-polygon/blob/master/index.js
export var pointInPolygon = (point : L.LatLng, polygon : L.Polygon) : Boolean => {
    "use strict";

    var latLngs = polygon.getLatLngs();
    var n = latLngs.length;
    var x = point.lat, y = point.lng;

    var inside = false;
    for (var i = 0; i < n; i++) {
        var j = (i + n - 1) % n;
        var xi = latLngs[i].lat, yi = latLngs[i].lng;
        var xj = latLngs[j].lat, yj = latLngs[j].lng;

        //      *
        //     /
        // *--/----------->>
        //   *
        // Check that
        //
        // 1.  yi and yj are on opposite sites of a ray to the right
        // 2.  the intersection of the ray and the segment is right of x
        var intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);

        if (intersect) {
            inside = !inside;
        }
    }

    return inside;
};
