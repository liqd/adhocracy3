/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

// code comes from https://github.com/substack/point-in-polygon/blob/master/index.js
export function pointInPolygon(point : number[], polygon: number[][]) : Boolean {
    "use strict";

    var x = point[1], y = point[0];

    var inside = false;
    for (var i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        var xi = polygon[i][0], yi = polygon[i][1];
        var xj = polygon[j][0], yj = polygon[j][1];
        var intersect = ((yi > y) !== (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) {
            inside = !inside;
        }
    }

    return inside;
}
