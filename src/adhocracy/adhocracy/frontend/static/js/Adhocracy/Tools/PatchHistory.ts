// version history chart

define("Adhocracy3/VersionGraph", ["require", "exports", "module", "d3"], function() {


    // module state.  this should be much smaller and cleaner.

    var width = 600;
    var height = 150;

    var previous_version = null;
    var current_version = null;

    var svg;
    var tooltip;
    var link;
    var node;

    var force = d3.layout.force()
        .charge(-120)
        .linkDistance(60)
        .size([width, height]);


    // helpers

    function drawArrow(d) {
            var node_width = 18;
            var node_height = 18;

            function edge_length(x, y) {
                return Math.sqrt(x * x, y * y);
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
            var arrow_size2 = arrow_size * 2 / 3;
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

    // move every node into its graph region: ancestors to the left,
    // siblings onto the middle line, and descentants and descentants
    // of siblings to the right.  also, enforce screen width and
    // height.
    function enforceRegion(d) {
        var x, y;
        var pad = 15;

        // app region (non-negotiable border)
        forceIntoRegion(d, 0, 0, width, height, pad, pad);  // XXX: use bbounds to get this more accurate.

        // history region
        switch (d.history_phase) {
        case("current"):
            x = width / 2;
            y = height / 2;
            break;
        case("ancestor"):
            x = d.x > (width / 2 - pad) ? (width / 2 - pad) : d.x;
            y = d.y;
            break;
        case("sibling"):
        case("descendant"):
            // siblings behave like descentants: we only distinguish
            // between "is part of the current version's history" and
            // "is not".  siblings and descendants are in the latter
            // category.

            x = d.x < (width / 2 + pad) ? (width / 2 + pad) : d.x;
            y = d.y;
            break;
        default:
            console.log(d.history_phase);
            throw "internal error";
        };
        pullTowardsPoint(d, x, y, 0.1);
    }

    function forceIntoRegion(d, xmin, ymin, xmax, ymax, xpad, ypad) {
        if (d.x < xmin + xpad) { d.x = xmin + xpad; } else
        if (d.x > xmax - xpad) { d.x = xmax - xpad; };
        if (d.y < ymin + ypad) { d.y = ymin + ypad; } else
        if (d.y > ymax - ypad) { d.y = ymax - ypad; };
    }

    function pullTowardsPoint(d, x, y, distFraction) {
        d.x += (x - d.x) * distFraction;
        d.y += (y - d.y) * distFraction;
    }


    // user callbacks (can be set via version graph object returned in
    // module main).

    // refresh events can be triggered both by the graph itself and by
    // the surrounding app.  if the surrounding app wants to refresh,
    // it calls the refresh method of the object returned by the
    // constructor of this module.  if it wants to act on a refresh
    // event triggered by the graph, it can register this callback
    // with the cb_refresh method of that object.
    var usr_cb_refresh   = function(d) { return; };

    // mouse click event handler
    var usr_cb_click     = function(d) { return; };

    // mouse double click event handler
    var usr_cb_dblclick  = function(d) { return; };


    // hard-wired callbacks (if available and after everything else,
    // these invoke user callbacks).

    var onNodeClick = function(d) {
        usr_cb_click(d);
    };

    var onNodeDblClick = function(nodes, mkLinks) {
        return function(d) {
            usr_cb_refresh(d.version, 2);
            usr_cb_dblclick(d);
        };
    };

    var onNodeMouseOver = function(d) {
        // d.fixed = true;  // XXX: this makes the graph go insane.  why?
    };

    var onNodeMouseMove = function(d) {
        // tooltip
            // .style("left", d3.event.pageX + "px")
            // .style("top", d3.event.pageY + "px");

        tooltip.select("pre")
            .text(JSON.stringify(d, null, 2));

        tooltip.transition()
            .duration(100)
            .style("opacity", 1);
    };

    var onNodeMouseOut = function(d) {
        // d.fixed = false;

        tooltip.transition()
            .duration(1800)
            .style("opacity", 0);
    };


    // XXX: shift+doublclick: delete version?
    // XXX: ctrl+shift+doublclick: compount versions?
    // XXX: ctrl+shift+alt+doubleclick: create new node and merge previous node with double-clicked node.


    // init, refresh, tick: the core d3js.force setup

    function init(domId) {

        // XXX: how do i remove the text from <div> element body?

        svg = d3.select(domId).append("svg")
            .attr("width", width)
            .attr("height", height);
        tooltip = d3.select(domId).append("div")
            .attr("class", "tooltip")
            .style("left", "800px")
            .style("top", "100px")
            .style("opacity", 0);
        tooltip.append("pre");
    };

    function refresh(nodes, mkLinks, version, recursionDepth) {
        console.assert(typeof version === "string");
        if (!(recursionDepth > 0)) { return; }

        links = mkLinks(nodes);

        console.assert(svg !== undefined);

        svg.selectAll(".node").data([]).exit().remove();
        svg.selectAll(".link").data([]).exit().remove();
        // XXX: can i remove nodes/links from right before calling
        // force.start(), and avoid re-creating unchanged ones?

        link = svg.selectAll(".link")
            .data(links)
            .enter().append("path")
            .attr("class", "link")
            .style("stroke-width", 3);

        node = svg.selectAll(".node")
            .data(nodes)
            .enter().append("circle")
            .attr("class", function(d) {
                return "node " + d.history_phase;
            })
            .attr("r", function(d) {
                if (d.history_phase === "current") {
                    return 15;
                } else {
                    return 10;
                }
            })
            .call(force.drag)
            .on("click",     onNodeClick)
            .on("dblclick",  onNodeDblClick(nodes, mkLinks))
            .on("mouseover", onNodeMouseOver)
            .on("mousemove", onNodeMouseMove)
            .on("mouseout",  onNodeMouseOut);

        node.append("title")
            .text(function(d) { return d.name; });

        force
            .nodes(nodes)
            .links(links)
            .on("tick", tick)
            .start();

        usr_cb_refresh(version, recursionDepth - 1);
    };

    function tick() {
        force.nodes().forEach(enforceRegion);

        // commit moves of all nodes.
        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });

        //link.attr("x1", function(d) { return d.source.x; })
        //    .attr("y1", function(d) { return d.source.y; })
        //    .attr("x2", function(d) { return d.target.x; })
        //    .attr("y2", function(d) { return d.target.y; });

        link.attr("d", drawArrow);
    };


    // version graph object

    return {
        init: function(domId, nodes, mkLinks, current_version) {
            console.assert(typeof current_version === "string");

            init(domId);
            refresh(nodes, mkLinks, current_version, 1);
            return {
                refresh: refresh,

                // register callbacks
                cb_refresh:   function(f) { usr_cb_refresh   = f; },
                cb_click:     function(f) { usr_cb_click     = f; },
                cb_dblclick:  function(f) { usr_cb_dblclick  = f; }
            };
        }
    };
});


// (note to distant future self: if there are merges, we should make
// all edges not on some canonical miminum spanning tree infinitely
// elastic (probably have to not give them to force graph and render
// them entirely ourselves instead).  this way, it should be
// relatively easy to write a good physics rule set for
// planarasition. -mf)
