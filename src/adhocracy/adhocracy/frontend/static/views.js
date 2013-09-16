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

*/


(function($, obviel) {

    // for editing

    // FIXME: Put in seperate module
    // Adds fields to make a view settings object editable.
    ad.Editable = function(child) {
        var result = {
            edit: function(ev) {
                    this.el.render(this.obj, "edit");
                },
        };
        $.extend(result, child);
        return result;
    };

    obviel.view({
        iface: 'adhocracy.interfaces.IParagraph',
        name: 'edit',
        obvt: '<div data-render="form"></div><button data-on="click|preview">Preview</div>',
        before: function() {
            this.obj.form = toForms(this.obj);
        },
        preview: function() {
            // FIXME: How do we get the real value?
            value = document.getElementById('obviel-field-auto0-text').value;
            this.obj.data['adhocracy#interfaces#IText'].text = value;
            this.el.render(this.obj);
        }
    });

    // end editing


    // Pool:
    obviel.view({
        iface: 'adhocracy.interfaces.IPool',
        obvtUrl: 'templates/IPool.obvt',
    });

    // Versionables
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
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
    var interfaces = ["IProposalContainer", "IParagraphContainer"];
    for (i in interfaces) {
        name = interfaces[i];
        obviel.view({
            iface: 'adhocracy.interfaces.' + name,
            name: 'small',
            obvtUrl: 'templates/IName.small.obvt'
        });
    };

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IProposal',
        obvtUrl: 'templates/IProposal.obvt',
    }));

    obviel.view(ad.Editable({
        iface: 'adhocracy.interfaces.IParagraph',
        obvtUrl: 'templates/IParagraph.obvt',
    }));

    obviel.view({
        iface: 'adhocracy.interfaces.INodeVersions',
        obvtUrl: "templates/INodeVersions.obvt"
    });

    obviel.view({
        iface: "formlist",
        obvt: '<div data-repeat="elements" data-render="@."></div>'
    });

    obviel.view({
        iface: 'debug_links',
        obvtUrl: 'templates/debug_links.obvt'
    });

}) (jQuery, obviel);
