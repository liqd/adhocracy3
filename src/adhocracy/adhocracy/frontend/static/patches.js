(function($, obviel) {

    // set up static, local proposal db (this is only interesting to
    // get a clean, self-contained test environment)

    var cache = {
          ahezwipfjfcj: { title: 'title', follows: null,           text: 'ahezwipfjfcj' },
          apldzspbndey: { title: 'title', follows: 'ahezwipfjfcj', text: 'apldzspbndey' },
          fiaylgffeirt: { title: 'title', follows: 'ahezwipfjfcj', text: 'fiaylgffeirt' },
          invxawjxxwcb: { title: 'title', follows: 'fiaylgffeirt', text: 'invxawjxxwcb' },
          njeaqgflnvnp: { title: 'to-tl', follows: 'fiaylgffeirt', text: 'njeaqgflnvnp' },
          pufpxzegrxdi: { title: 'to-tl', follows: 'njeaqgflnvnp', text: 'pufpxzegrxdi' },
          qqfbxcifvrkg: { title: 'tu-tl', follows: 'pufpxzegrxdi', text: 'qqfbxcifvrkg' }
    };

    // global: path to initial version.  this is displayed after page load.
    var prop_initial_version = 'ahezwipfjfcj';

    // global: current and previous displayed / edited versions.
    // previous is used for cleaning up chart structure.
    var prop_current_version = prop_initial_version;
    var prop_previous_version;

    // call initCache every time new objects have been added to update
    // internal the data structure.  in particular, call this function
    // from createNewVersion.  this is not very efficient, but makes
    // the source easier to read, which is the priority for now.
    var initCache = function(cache) {
        // inject version strings and followed_by edges
        Object.keys(cache).forEach(function(k) {
            cache[k].version = k;
            cache[k].followed_by = [];
        });
        Object.keys(cache).forEach(function(k) {
            var parent = cache[k].follows;
            if (parent !== null) {
                cache[parent].followed_by.push(k)
            }
        });

        // ifaces
        Object.keys(cache).forEach(function(k) {
            cache[k].ifaces = ['proposal'];
        });

        // render_state (edit|display)
        Object.keys(cache).forEach(function(k) {
            cache[k].render_state = 'display';
        });
    };

    // every version in the cache has an attribute called
    // history_phase that states whether it is an ancestor of the
    // current version, or a descentant, or a sibling (has a common
    // parent with the current version, or is the descentant of a
    // sibling).  this function refreshes this attribute.
    var refreshHistoryPhases = function(cache, current_version) {
        Object.keys(cache).forEach(function(version) {
            cache[version].history_phase = 'sibling';
        });
        cache[current_version].history_phase = 'current';
        ancestors(cache[current_version]).forEach(function(version) {
            cache[version].history_phase = 'ancestor';
        });
        descendants(cache[current_version]).forEach(function(version) {
            cache[version].history_phase = 'descentant';
        });
    }

    var ancestors = function(obj) {
        if (obj.follows) {
            var result = [];
            result.push(cache[obj.follows].version);
            result.concat(ancestors(cache[obj.follows]));
            return result;
        } else {
            return [];
        }
    };

    var descendants = function(obj) {
        var result = [];
        obj.followed_by.forEach(function(version) {
            if (result.indexOf(version) < 0) {  // if running into a cycle, don't traverse it again
                result.push(version);
                result.concat(descendants(cache[version]));
            }
        });
        return result;
    };

    var commitNewVersion = function(obj) {
        var new_ver = createNewVersion();
        var new_obj = { title: obj.title, follows: obj.version, text: obj.text };

        cache[new_ver] = new_obj;
        initCache(cache);

        return new_obj;
    };

    var createNewVersion = function() {
        var v = '';
        for (i = 0; i < 12; i++) {
            c = String.fromCharCode(Math.floor(Math.random() * 26) + 'a'.charCodeAt(0));
            v = v + c.toString();
        };
        return v;
    };


    // obviel views

    obviel.view({
        iface: 'proposal',
        name:  'display',
        obvt:  '<h1>{title}</h1>' +
               '<ul>' +
               '<li>this version: <a href="#{version}"><tt>{version}</tt></a></li>' +
               '<li>follows version: <a href="#{follows}"><tt>{follows}</tt></a></li>' +
               '<li>followed_by versions:<span data-repeat="followed_by"><tt> <a href="#{@.}">{@.}</a></tt></span></li>' +
               '</ul>' +
               '<textarea readonly>{text}</textarea>' +

               // XXX according to obviel.org/en/1.0/templates.html,
               // this here should work, but it doesn't:
               //
               // Object.keys(cache).forEach(function(k) {
               //     cache[k].textarea_attributes = [{name: 'readonly', value: 'true'}];
               // });
               //
               // '<textarea><span data-repeat="textarea_attributes" data-attr="{name}" data-value="{value}"/>{text}</textarea>' +
               //
               // (or am i being stupid again? -mf)
               //
               // this is sad because if it worked, we might be able
               // to use one template for both display and render.
               //
               // the real problem here though is that textarea
               // doesn't comply with the xml syntax rule that '<elem
               // attr>' is equivalent to '<elem attr="">'.

               '<hr>' +
               '<button data-on="click|startEdit">edit</button>',

        startEdit: function(ev) {
            this.obj.render_state = 'edit';
            refresh(this.obj.version);
        }
    });

    obviel.view({
        iface: 'proposal',
        name:  'edit',
        obvt:  '<h1>{title}</h1>' +
               '<ul>' +
               '<li>this version: <a href="#{version}"><tt>{version}</tt></a></li>' +
               '<li>follows version: <a href="#{follows}"><tt>{follows}</tt></a></li>' +
               '<li>followed_by versions:<span data-repeat="followed_by"><tt> <a href="#{@.}">{@.}</a></tt></span></li>' +
               '</ul>' +
               '<textarea id="proposal_text">{text}</textarea>' +
               '<hr>' +
               '<button data-on="click|commit">create new version</button>',

        commit: function(ev) {
            this.obj.render_state = 'display';
            var new_obj = commitNewVersion(this.obj);

            // update new object from dom
            new_obj.text = document.getElementById("proposal_text").value;

            // show new version
            refresh(new_obj.version);


            // XXX: make title editable.
        }
    });


    // error handling

    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });


    // version history chart

    var onVersionClick = function(d) {
        console.log('onVersionClick');
    };
    var onVersionDoubleClick = function(d) {
        console.log('onVersionDoubleClick');
        refresh(d.version);
    };

    var onVersionMouseOver = function(d) {
        console.log('onVersionMouseOver');
        // d.fixed = true;  // XXX: this makes the graph go insane.  why?
    };

    var onVersionMouseMove = function(d) {
        console.log('onVersionMouseMove');
    };

    var onVersionMouseOut = function(d) {
        console.log('onVersionMouseOut');
        // d.fixed = false;
    };


    // XXX: shift+doublclick: delete version?
    // XXX: ctrl+shift+doublclick: compount versions?
    // XXX: ctrl+shift+alt+doubleclick: create new node and merge previous node with double-clicked node.


    var versionChart = (function(nodeClick, nodeDoubleClick, nodeMouseOver, nodeMouseMove, nodeMouseOut) {
        var width = 600;
        var height = 150;
        var color = d3.scale.category20();

        var force = d3.layout.force()
            .charge(-120)
            .linkDistance(60)
            .size([width, height]);

        var svg;
        var tooltip;
        var link;
        var node;

        var init = function() {

            // XXX: how do i remove the text from <div> element body?

            svg = d3.select("#version_chart").append("svg")
                .attr("width", width)
                .attr("height", height);
            tooltip = d3.select("#version_chart").append("div")
                .attr("class", "tooltip")
                .style("left", "800px")
                .style("top", "100px")
                .style("opacity", 0);
            tooltip.append("pre");
        };

        var refresh = function() {
            console.assert(svg !== undefined);

            svg.selectAll(".node").data([]).exit().remove();
            svg.selectAll(".link").data([]).exit().remove();

            var nodes = Object.keys(cache).map(function(k) { return cache[k]; });
            var links = [];
            nodes.forEach(function(n) {
                if (typeof n.follows == 'string') {
                    var source = nodes.indexOf(cache[n.follows]);
                    var target = nodes.indexOf(n);
                    links.push({ source: source, target: target });
                }
            });

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
                    if (d.version == prop_current_version) {
                        return 15;
                    } else {
                        return 10;
                    }
                })
                .style("fill", function(d) {
                    return color(d.history_phase);
                })
                .call(force.drag)
                .on("click", nodeClick)
                .on("dblclick", nodeDoubleClick)
                .on("mouseover", nodeMouseOver)
                .on("mousemove", function(d) {
                    // tooltip
                        // .style("left", d3.event.pageX + "px")
                        // .style("top", d3.event.pageY + "px");

                    tooltip.select("pre")
                        .text(JSON.stringify(d, null, 2));

                    tooltip.transition()
                        .duration(100)
                        .style("opacity", 1);

                    return nodeMouseMove(d);
                })
                .on("mouseout", function(d) {
                    tooltip.transition()
                        .duration(1800)
                        .style("opacity", 0);

                    return nodeMouseOut(d);
                });

            node.append("title")
                .text(function(d) { return d.name; });

            force
                .nodes(nodes)
                .links(links)
                .on("tick", tick)
                .start();
        };

        var tick = function() {
            // keep current version frozen in one place, no matter what force layout sais.
            cache[prop_current_version].x = width / 2;
            cache[prop_current_version].y = height / 2;

            // commit moves of all nodes.
            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });

            //link.attr("x1", function(d) { return d.source.x; })
            //    .attr("y1", function(d) { return d.source.y; })
            //    .attr("x2", function(d) { return d.target.x; })
            //    .attr("y2", function(d) { return d.target.y; });

	    link.attr("d", function(d) {
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
	    });
        };

        return { init: init, refresh: refresh };
    })(onVersionClick, onVersionDoubleClick, onVersionMouseOver, onVersionMouseMove, onVersionMouseOut);


    // main

    var refresh = function(version) {
        $('#main').render(cache[version], cache[version].render_state);
        prop_previous_version = prop_current_version;
        prop_current_version = version;
        refreshHistoryPhases(cache, prop_current_version);
        versionChart.refresh();
    };

    $(window).bind('hashchange', function(event) {
        // (this event is triggered only when following the href
        // anchors, not when clicking on version nodes in the graph)
        var version = event.fragment;
        console.log("hashchange: " + version);
        refresh(version);
    });

    $(document).ready(function() {
        initCache(cache);
        versionChart.init();
        refresh(prop_initial_version);
    });


}) (jQuery, obviel);
