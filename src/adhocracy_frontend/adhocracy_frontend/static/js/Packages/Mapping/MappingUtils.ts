// code comes from https://github.com/substack/point-in-polygon/blob/master/index.js
export var pointInPolygon = (point : number[], polygon : number[][]) : Boolean => {
    "use strict";

    var n = polygon.length;
    var x = point[1], y = point[0];

    var inside = false;
    for (var i = 0; i < n; i++) {
        var j = (i + n - 1) % n;
        var xi = polygon[i][0], yi = polygon[i][1];
        var xj = polygon[j][0], yj = polygon[j][1];

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
