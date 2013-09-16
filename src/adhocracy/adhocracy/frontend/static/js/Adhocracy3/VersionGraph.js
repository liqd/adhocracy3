// version history chart

define('Adhocracy3/VersionGraph', ['require', 'exports', 'module', 'd3'], function() {


    // module state.  this should be much smaller and cleaner.

    var width = 600;
    var height = 150;
    var color = d3.scale.category20();

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


    // user callbacks (can be set via version graph object returned in
    // module main).

    var usr_cb_click = function(d) { };
    var usr_cb_dblclick = function(d) { };


    // hard-wired callbacks (if available and after everything else,
    // these invoke user callbacks).

    var onNodeClick = function(d) {
        console.log('onNodeClick');

        usr_cb_click(d);
    };

    var onNodeDoubleClick = function(nodes, mkLinks) {
        return function(d) {
            console.log('onNodeDoubleClick');

            refresh(nodes, mkLinks, d);
            usr_cb_dblclick(d);
        };
    };

    var onNodeMouseOver = function(d) {
        console.log('onNodeMouseOver');
        // d.fixed = true;  // XXX: this makes the graph go insane.  why?
    };

    var onNodeMouseMove = function(d) {
        console.log('onNodeMouseMove');

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
        console.log('onNodeMouseOut');
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

    function refresh(nodes, mkLinks, current_version_) {
        links = mkLinks(nodes);
        previous_version = current_version;
        current_version = current_version_;

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
            .attr("class", "node")
            .attr("r", function(d) {
                if (d.history_phase == 'current') {
                    return 15;
                } else {
                    return 10;
                }
            })
            .style("fill", function(d) {
                return color(d.history_phase);
            })
            .call(force.drag)
            .on("click",     onNodeClick)
            .on("dblclick",  onNodeDoubleClick(nodes, mkLinks))
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
    };

    function tick() {
        // keep current version frozen in one place, no matter what force layout sais.
        current_version.x = width / 2;
        current_version.y = height / 2;

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
            init(domId);
            refresh(nodes, mkLinks, current_version);
            return {
		refresh: refresh,

                // register callbacks
                cb_click:     function(f) { usr_cb_click     = f; },
                cb_dblclick:  function(f) { usr_cb_dblclick  = f; }
	    };
	}
    };
});
