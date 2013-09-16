require.config({
    baseUrl: "./js/",
    paths: {
        'jquery':            '../jquery-1.7.2',
        'jquery_datalink':   '../submodules/jquery-datalink/jquery.datalink',
        'jquery_ba_bbq':     '../submodules/jquery-bbq/jquery.ba-bbq',
        'obviel-templates':  '../submodules/obviel/src/obviel/obviel-template',
        'obviel':            '../submodules/obviel/src/obviel/obviel',
        'obviel-forms':      '../submodules/obviel/src/obviel/obviel-forms',
        'd3':                '../d3-3.2.8',
    },
    shim: {
        'jquery_datalink': {
            deps: ['jquery'],
            exports: 'jquery_datalink'
	},
        'jquery_ba_bbq': {
            deps: ['jquery'],
            exports: 'jquery_ba_bbq'
	},
        'obviel-templates': {
            deps: [],
            exports: 'obviel-templates'
	},
        'obviel': {
            deps: [],
            exports: 'obviel'
	},
        'obviel-forms': {
            deps: [],
            exports: 'obviel-forms'
	},
        'd3': {
            deps: [],
            exports: 'd3'
	}
    }
});

require([ 'jquery',
          'jquery_datalink',
          'jquery_ba_bbq',
          'obviel-templates',
          'obviel',
          'obviel-forms',
          'Adhocracy3/VersionGraph'
        ], function($, datalink, bbq, obviel_templates, obviel, obviel_forms, graph) {

(function() {


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
            result = result.concat(ancestors(cache[obj.follows]));
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
                result = result.concat(descendants(cache[version]));
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
            refresh(this.obj.version, true);
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
            refresh(new_obj.version, true);


            // XXX: make title editable.
        }
    });


    // error handling

    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });


    // version history chart

    // nodes must be generated from cache, so what passes to the graph
    // constructor is the object returned by mkNodes().
    var mkNodes = function() {
        var nodes = Object
            .keys(cache)
            .map(function(k) { return cache[k]; });

        // XXX: type check nodes.  (or better yet, do it in graph.init().)

        return nodes;
    }

    // links (edges) are generated from the node list, so what passes
    // to the graph constructor is (in contrast to mkNodes()) the
    // *function* mkLinks().
    var mkLinks = function(nodes) {
        var links = [];
        nodes.forEach(function(n) {
            if (typeof n.follows == 'string') {
                var source = nodes.indexOf(cache[n.follows]);
                var target = nodes.indexOf(n);
                links.push({ source: source, target: target });
            }
        });

        // XXX: type check links.  (see also mkNodes() above.)

        return links;
    }

    var versionGraph;


    // main

    var refresh = function(version, refreshVersionGraph) {
        // refresh updates the version graph, but is also registered
        // as a callback in the version graph for double click events.
        // in order to avoid infinite loops, there is a flag that can
        // switch off refreshing of the version graph if it already
        // happened.

        $('#main').render(cache[version], cache[version].render_state);
        refreshHistoryPhases(cache, version);
        if (refreshVersionGraph) {
	    versionGraph.refresh(mkNodes(), mkLinks, cache[version]);
	}
    };

    $(window).bind('hashchange', function(event) {
        // (this event is triggered only when following the href
        // anchors, not when clicking on version nodes in the graph)
        var version = event.fragment;
        console.log("hashchange: " + version);
        refresh(version, true);
    });

    $(document).ready(function() {
        initCache(cache);
        versionGraph = graph.init("#version_chart", mkNodes(), mkLinks, cache[prop_initial_version]);
        versionGraph.cb_dblclick(function(d) {
            refresh(d.version, false);
	});
        refresh(prop_initial_version, true);
    });


}) (); })



// XXX: visually partition version history in past, present, and
// future.  somehow.  use css as much as possible.
