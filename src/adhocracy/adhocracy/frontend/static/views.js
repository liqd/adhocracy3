/* notes from dinner discussion today (are these worth keeping?  where
 * should i move them?  -mf):

there should be a way to keep changes locally without posting them
right away.  something like a button that toggles between "edit" and
"display", and if there are local changes, the background colour
changes to "not saved", and two further buttons "submit changes" and
"discard changes" appear next to the "edit/display" button.  "submit"
and "discard" buttons also appear on super-structures; if the user has
edited a number of paragraphs, she can post a new version of the
entire document with one click.

there must be a way for the server to receive a batch of post requests
that are processed in one database "transaction" (not to be confused
with rest api transactions that need to be handled by client and
server cooperatively and are a total mess).

if the server receives a paragraph update (or several ones), it
performs the update to the containing document triggered by the
essence edge from paragraph to document, and possibly further updates.
all objects updated implicitly by the paragraph update are collected
into a dict that maps old versions (that are still up to date for all
the client knows) to new ones (that the client should know about).
this dict is sent to the client in the http response to the paragraph
update.

this does not address the problem that the server wants to tell the
client about changes by other users in real-time.  but that's an
unrelated problem: if a user changes a paragraph, she wants to go on
working on the changed version right away; if other users change
stuff, she wants to be notified as soon as possible, but (1) delays
are acceptable, and (2) she doesn't want the notifications to
interfere with her work.



Fri Sep 20 17:21:51 CEST 2013


marker interfaces are implemented by json objects that have a
content-type attribute and a data attribute that contains a list of
json objects implementing the supported do-er interfaces.

do-er interfaces are implemented by json objects that have
interface-dependent structure and contain the actual data.

marker and do-er interfaces are interleaved.  whatever that means.


to register multiple obviel-ifaces for multiple doer interfaces: there
is one default view, and


register following interfaces:

 - marker interface, 'default'
 - marker interface, 'edit'

for each do-er interface:

 - do-er-interface, 'default.do-er-interface'
 - do-er-interface, 'edit.do-er-interface'


trick: because there is no way of explicitly picking an interface if
several matching views are installed, each interface has both iface
and name set to the same string.  so we can choose via the name.
(this is for the doer interfaces.  marker interfaces are always listed
first in the ifaces attribute, so they are picked by default.)  views
always work on marker interface level.



// "do-er interface" => "property sheet interface"

model = {
ifaces: ["marker", "propsheet1", "propsheet2", ...]
}


views:

{ iface: 'marker', ... }
{ iface: 'propsheet1', name: 'propsheet1', ... }
{ iface: 'propsheet2', name: 'propsheet2', ... }



vererbung?  - obviel.extendsIface(parent, child).  requires server to send inheritance hierarchy to client, id




Mon Sep 23 10:46:27 CEST 2013

 . save button
 . reset button / keeping track of changes


the save button posts a changed model from the client back to the
server, creating a new version that is then retrieved and rendered by
the client.  (there may be performance considerations with this, but
for now this is how it is implemented.)

in order for the client to decide whether a model contains new data
that is not available on the server, each sub-tree may contain an
attribute __orig__ that contains a copy of the previous version of
that subtree.  "save" and "reset" are only available if __orig__
exists in some sub-tree.



*/


(function($, obviel) {

    // for editing

    // Adds fields to make a view settings object editable.
    // FIXME: Put in seperate module
    ad.Editable = function(view) {
        var result = {};
        if (typeof(view.name) == 'undefined' || view.name == 'default') {
            result.edit = function(ev) {
                this.el.render(this.obj, "edit");
            }
	};

        if (view.name == 'edit') {
            result.display = function(ev) {
                this.el.render(this.obj, "default");
            }
	};

        result.reset = function() {
            resetObj(this.obj)
        };

        result.save = function() {
            saveObj(this.obj)
        };

        $.extend(result, view);
        return result;
    };

    // FIXME: need separation between marker and do-er views.  perhaps even in rest api.

    function hasChanged(obj) {
        Object.keys(obj.data).forEach(function(k) {
            if ('__orig__' in obj.data[k]) {
                return true;
	    }
            // FIXME: recurse
	})
        return false;
    };

    function resetObj(obj) {
        console.log('resetObj');
        Object.keys(obj.data).forEach(function(k) {
            if ('__orig__' in obj.data[k]) {
                obj.data[k] = obj.data[k].__orig__;
                delete obj.data[k].__orig__;
	    }
            // FIXME: recurse
        });
    };

    function saveObj(obj) {
        // FIXME: notification field with a "paragraph saved" message.
        // FIXME: do not send __orig__ sub-trees over the net with the new version.

        var changes = collectChangedNodes(ad.repo, obj);
        console.log(changes);

        if (hasChanged(obj)) {
            console.log("POST");

            var payload = {
              'content_type': 'adhocracy.interfaces.IParagraph',
              'data': obj
            };

            var path = '';

            $.ajax(path, {
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                data: showjs(propcontainer),
                success: dummyHandler("2/success"),
                error:   dummyHandler("2/error")
              });

            // FIXME: it is not clear how to push trees of nodes.

            // render newly saved object as returned from server.
            // (needs to be moved over the wire once to straighten out
            // meta data.)

	}
    };

    function dummyHandler(name) {
        return function(jqxhr, textstatus, errorthrown) {
            console.log(name + ": [" + showjs(jqxhr) + "][" + textstatus + "][" + errorthrown + "]")
        }
    };

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.display.obvt',

        // FIXME: in IParagraph.*.obvt, render "reset", "save" buttons
        // conditionally only if __orig__ exists.
    }));

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        name: 'edit',
        obvtUrl: 'templates/IParagraph.edit.obvt',

        display: function() {
            value = this.el[0].getElementsByClassName('__widget__')[0].value;

            var model = this.obj.data['adhocracy#interfaces#IText'];
            model.__orig__ = model;  // FIXME: use deep copy.  better yet: use 'has_changed' marker and implement 'reset' button with "render('url')".
            model.text = value;

            this.el.render(this.obj);
        },
    }));

/*
    obviel.view(ad.Editable({
                   // FIXME: display/default and edit views should
		   // either both be on IParagraph or both on IText.
        iface: 'adhocracy.interfaces.IText',
        name: 'default',
        obvt: '<pre>{@.}</pre>' +
              '<textarea>{text}</textarea>' +
              '<button data-on="click|preview">preview</button>' +
              '',

        display: function() {
            value = this.el[0].children[1].value;
            this.obj.text = value;
            this.el.render(this.obj);
        }
    }));
*/


    // Pool:
    obviel.view({
        iface: 'adhocracy.interfaces.IPool',
        obvtUrl: 'templates/IPool.obvt',
    });

    // Versionables
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
    // FIXME: all for loops in this file are probably bogus; what they
    // do is determine the data model by assigning interfaces to
    // models.  this should be entirely done by the server.
    for (i in interfaces) {
        name = interfaces[i];
        // console.log(('adhocracy.interfaces.' + name));
        obviel.view({
            iface: ('adhocracy.interfaces.' + name),
            before: function() {
                this.obj._versions_path = this.obj.meta.path + "/_versions";
            },
            obvt: '<div data-render="_versions_path"></div>',
        });
    };

    // small views for named items
    obviel.view({
        iface: 'adhocracy.interfaces.IName',
        name: 'small.adhocracy.interfaces.IName',
        obvtUrl: 'templates/IName.small.obvt'
    });

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view({
        iface: 'adhocracy.interfaces.INodeVersions',
        obvtUrl: "templates/INodeVersions.obvt"
    });

    obviel.view({
        iface: 'debug_links',
        obvtUrl: 'templates/debug_links.obvt'
    });

}) (jQuery, obviel);
