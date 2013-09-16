define('Adhocracy3/VersionGraph', ['require', 'exports', 'module'], function() {

    return {
        drawArrow: function(d) {
            var node_width = 18;
            var node_height = 18;

            function edge_length(x, y) {
                return Math.sqrt(x*x, y*y);
            }

            var sourcex = d.source.x + node_width  / 2;
            var sourcey = d.source.y + node_height / 2;
            var targetx = d.target.x + node_width  / 2;
            var targety = d.target.y + node_height / 2;

            var dx = targetx - sourcex;
            var dy = targety - sourcey;
            var r = 0.08;

            // i tried to figure out what r needs to be to hit
            // exactly the edge of the icon at 19pxx19px, but i
            // failed miserably.  :(
            //
            // r = Math.max((node_width / 2) / Math.abs(dx), (node_width / 2) / Math.abs(dy));
            // if (r > 1) { r = 0.1; }
            // (2 + edge_length(node_width, node_height)) / edge_length(dx, dy);
            // (this transforms radius in pixels to radius in fraction of total edge length.)

            // start point and end point
            var sx = sourcex + dx * r;
            var sy = sourcey + dy * r;
            var tx = targetx - dx * r;
            var ty = targety - dy * r;

            var arrow_size = 5;
            var arrow_size2 = arrow_size*2/3;
            return ("M " + sx + " " + sy + " " +
                    "L " + tx + " " + ty + " " +
                    "M " + (tx - arrow_size2) + " " + (ty - arrow_size2) + " " +
                    "L " + (tx + arrow_size2) + " " + (ty + arrow_size2) + " " +
                    "M " + (tx - arrow_size2) + " " + (ty + arrow_size2) + " " +
                    "L " + (tx + arrow_size2) + " " + (ty - arrow_size2) + " " +
                    "M " + (tx - arrow_size) + " " + (ty) + " " +
                    "L " + (tx + arrow_size) + " " + (ty) + " " +
                    "M " + (tx) + " " + (ty + arrow_size) + " " +
                    "L " + (tx) + " " + (ty - arrow_size) + " " +
                    "");
          }
    };
});
