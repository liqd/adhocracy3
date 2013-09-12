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

    // path to initial version.  this is displayed after page load.
    var prop_initial_version = 'ahezwipfjfcj';

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

    initCache(cache);


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


    // d3js history

    var versionChart = (function() {
        // cloned from http://bl.ocks.org/mbostock/4062045

	var width = 960;
	var height = 500;
        var color = d3.scale.category20();

        var force = d3.layout.force()
            .charge(-120)
            .linkDistance(30)
            .size([width, height]);

        var svg;
        var link;
        var node;

        force.on("tick", function() {
          link.attr("x1", function(d) { return d.source.x; })
              .attr("y1", function(d) { return d.source.y; })
              .attr("x2", function(d) { return d.target.x; })
              .attr("y2", function(d) { return d.target.y; });

          node.attr("cx", function(d) { return d.x; })
              .attr("cy", function(d) { return d.y; });
        });

        var init = function() {
            svg = d3.select("#version_chart").append("svg")
                .attr("width", width)
                .attr("height", height);
	};

        var refresh = function() {
            console.assert(svg !== undefined);

            svg.selectAll(".node").data([]).exit().remove();
            svg.selectAll(".link").data([]).exit().remove();

            var nodes = Object.keys(cache);
            var links = [];
            nodes.forEach(function(n) {
                console.assert(typeof cache[n] !== 'undefined', "n is undefined");
                console.assert(typeof cache[n].follows !== 'undefined', "n.follows is undefined");

                if (cache[n].follows !== null) {
                    var source = nodes.indexOf(cache[cache[n].follows].version);
                    var target = nodes.indexOf(n);
                    links.push({ source: source, target: target });
		}
	    });

            link = svg.selectAll(".link")
                .data(links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width", 3);

            node = svg.selectAll(".node")
                .data(nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 5)
                .style("fill", 4)
                .call(force.drag);

            node.append("title")
                .text(function(d) { return d.name; });

            force
                .nodes(nodes)
                .links(links)
                .start();
        };

        return { init: init, refresh: refresh };
    })();


    // main

    var refresh = function(path) {
        $('#main').render(cache[path], cache[path].render_state);
        versionChart.refresh(path);
    };

    $(window).bind('hashchange', function(ev) {
        var path = ev.fragment;
        console.log("hashchange: " + path);
        refresh(path);
    });

    $(document).ready(function() {
        versionChart.init();
        refresh(prop_initial_version);
    });


}) (jQuery, obviel);
