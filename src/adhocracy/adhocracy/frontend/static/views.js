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



vererbung?  - obviel.extendsIface.  requires server to send inheritance hierarchy to client, id







*/


(function($, obviel) {

    // for editing

    // Adds fields to make a view settings object editable.
    // FIXME: Put in seperate module
    // FIXME: 'save' and 'reset' buttons should pop up whenever in 'preview' mode.
    //        (you are in preview mode when things have changed w.r.t. model version from server.)
    ad.Editable = function(view) {
        var result = {};
        if (view.name == 'default') {
            result.edit = function(ev) {
                this.el.render(this.obj, "edit");
            }
	};
        if (view.name == 'edit') {
            result.display = function(ev) {
                this.el.render(this.obj, "default");
            }
	};
        $.extend(result, view);
        return result;
    };

    // FIXME: need separation between marker and do-er views.  perhaps even in rest api.

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.obvt',
    }));

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        name: 'edit',
        obvUrl: 'templates/IParagraph.edit.obvt',

        display: function() {
            value = this.el[0].getElementsByClassName('__widget__')[0].value;
            this.obj.data['adhocracy#interfaces#IText'].text = value;

            this.el.render(this.obj);
        }
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
        console.log(('adhocracy.interfaces.' + name));
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
