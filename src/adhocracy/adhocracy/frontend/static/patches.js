(function($, obviel) {

    // set up static, local proposal db

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

    var init_cache = function(cache) {
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
    }

    init_cache(cache);


    // views

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
               '[editbutton]'
    });


    // error handling

    obviel.httpErrorHook(function(xhr) {
        console.log("httpError:");
        console.log(xhr);
    });


    // refresh page

    var refresh = function(path) {
        $('#main').render(cache[path], cache[path].render_state);
    };

    $(window).bind('hashchange', function(ev) {
        var path = ev.fragment;
        console.log("hashchange: " + path);
        refresh(path);
    });

    $(document).ready(function() {
        refresh(prop_initial_version);
    });


}) (jQuery, obviel);
