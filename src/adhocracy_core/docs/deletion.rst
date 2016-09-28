.. _api-deletion:

Deleting Resources
==================

Anyone with the *delete_resource* permission can *delete* it by using
the HTTP DELETE verb.  Deleted resources can not be recovered.

Deleting an existing resource is only possible for updatable
resources like Simple, Pools, Items, i.e. *not* for Versions as this would mess up the version
:term:`DAG` and *not* for AssetDownloads.

The effect of deleting is as follows:

* All child/descendant resources (whose resource path includes the path
  of the deleted ancestor as prefix) are also deleted.
* Deleted resources are no longer listed in parent pools or search
  queries.
* If the frontend attempts to retrieve a *deleted* resource via
  GET, the backend responds with HTTP status code *404 Not Found*, just
  as if the resource had never existed.
* *Deleted* resources may not be referenced from other
  resources. If the frontend follows an outdated references it must therefore
  be prepared to encounter *404 Not Found* responses and deal with them
  appropriately (e.g. by silently skipping them or by showing an
  explanation such as "Comment deleted").
* *DELETE* http method is idempotent

Hiding Resources
================

Apart from physically deleting a resource, it can also be marked as
"hidden" using a boolean field (flag) defined in the
*adhocracy_core.sheets.metadata.IMetadata* sheet. It default to false.
If this sheet is omitted when POSTing new resources, the default value
is used.

The usecase for deleting is that users want to withdraw some content.
The usecase for hiding is that moderators want to hide unapproriate
content.

Hiding an existing resource is only possible for updatable
resources, i.e. *not* for Versions (which are immutable and hence don't
allow PUT).

Anyone with the *hide* permission (typically granted to the manager
role) can *hide* a resource by PUTting an update with *IMetadata { hidden:
true }*. Likewise they can un-hide a hidden resource by PUTting an update with
*IMetadata { hidden: false }*. Nobody else can change the value of the
*hidden* field.

The effect of these flags is as follows:

* A positive value of the *hidden* flags is inherited by
  child/descendant resources (whose resource path includes the path of
  the hidden ancestor as prefix). Hence a *hidden* resource is one that
  has its own *hidden* flag set to true or that has an ancestor whose
  *hidden* flag is true.
* Normally, only resources that are not *hidden* are listed in parent
  pools and search queries.
* FIXME Not implemented yet, since the frontend doesn't yet need it: The
  parameter *include=hidden* can be used to include hidden resources in
  pool listings and other search queries.  If its value is *hidden*,
  resources will be found regardless of the value of their *hidden*
  flag.  However, only those with *hide* permission are ever
  able to view the contents of hidden resources.  It's also possible to
  set *include=visible* to get only non-hidden
  resources, but it's not necessary since that is the default.
* If the frontend attempts to retrieve a *hidden* resource via GET, the
  backend normally responds with HTTP status code *410 Gone*.
  FIXME Not implemented yet, since the frontend doesn't yet need it: The
  frontend can override this by adding the parameter *include=hidden* to
  the GET request, just as in search queries.  Managers (those with
  *hide* permission) can view hidden resources in this way.
  Those without this permission will still get a *410 Gone* if the
  resource is hidden.
* The body of the *410 Gone* is a small JSON document that explains why
  the resource is gone (for future use if there may be other reasons
  than *hidden*). It also shows who made the last change to the resource
  and when::

      { 'reason': 'hidden',
        'modified_by': '<path-to-user>',
        'modification_date': '<timestamp>'}

  Often the last modification will have been the hiding of the resource,
  but there is no guarantee that this is always the case.  Especially,
  the resource may be marked as hidden because one of its ancestors was
  hidden (as that status is inherited). In that case, the person who
  last modified the child resource likely has nothing to do with the
  person who hid the ancestor resource.
* *Hidden* resources may still be referenced from other resources. If
  the frontend follows such references it must therefore be prepared to
  encounter *410 Gone* responses and deal with them appropriately (e.g.
  by silently skipping them or by showing an explanation such as
  "Comment deleted").
* FIXME Not implemented yet, since the frontend doesn't yet need it.
  *Hidden* resources will normally not be shown in backreferences, which
  are calculated on demand. The *include=hidden* parameter can be used
  to change that and include backreferences to hidden resources. The
  same restrictions apply, i.e. normal users can use this parameter to
  find out whether hidden backreferences exist, but they won't be able
  to see their contents. In any case the frontend should be prepared to
  deal with *410 Gone* when following backreferences in the same way as
  when following forward reference -- even if it didn't explicitly ask
  to include them, they might show up due to caching.

FIXME We should extend the Meta API to expose the distinction between
references and backreferences to the frontend, currently only the backend
knows this.

Notes:

* This document is about deletion of resources (JSON documents).
  Deletion of uploaded assets (images, PDFs etc.) is outside its current
  scope.
* Currently, the hidden status of resources isn't treated as special by
  the Websocket server. So, if an resource is flagged as hidden, a
  "modified" event is sent to subscribers of that resource and a
  "modified_child" event is sent to subscribers of the parent pool.
  FIXME At same point in the future, we might want to change that and
  send "removed"/"removed_item" messages instead.


A Censorship Example
--------------------

Lets put the above theory into practice by hiding (censoring) some content!

Some imports to work with rest api calls::

    >>> from pprint import pprint

Start adhocracy app and log in some users::

    >>> log = getfixture('log')
    >>> anonymous = getfixture('app_anonymous')
    >>> participant = getfixture('app_participant')
    >>> moderator = getfixture('app_moderator')
    >>> admin = getfixture('app_admin')
    >>> rest_url = getfixture('rest_url')

Lets create some content::

    >>> data = {'content_type': 'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name':  'pool2'}}}
    >>> resp = admin.post('/', data)
    >>> data = {'content_type': 'adhocracy_core.resources.process.IProcess',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'child'}}}
    >>> resp = admin.post('/pool2', data)
    >>> data = {'content_type': 'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'pool1'}}}
    >>> resp = admin.post('/', data)
    >>> data = {'content_type': 'adhocracy_core.resources.process.IProcess',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'child'}}}
    >>> resp = admin.post('/pool1', data)
    >>> data = {'content_type': 'adhocracy_core.resources.document.IDocument',
    ...         'data': {}}
    >>> resp = participant.post('/pool1/child', data)
    >>> document_creator = participant.user_path
    >>> document_item = resp.json['path']
    >>> document_first_version = resp.json['first_version_path']


As expected, we can retrieve the pool and its child::

    >>> resp = anonymous.get('/pool2').json
    >>> 'data' in resp
    True
    >>> resp = anonymous.get('/pool2/child').json
    >>> 'data' in resp
    True

Both pools show up in the pool sheet::

    >>> resp = anonymous.get('/',  params={'elements': 'paths'}).json
    >>> pprint(sorted(resp['data']['adhocracy_core.sheets.pool.IPool']
    ...                        ['elements']))
    ['.../pool1/',.../pool2/'...

Lets check whether we have the permission to delete resources.
The person who has created a resource (creator role) has the right to delete
it::

    >>> resp = participant.options(document_item).json
    >>> 'DELETE' in resp
    True

But they cannot hide it::

    >>> 'PUT' not in resp
    True

-- that special right is reserved to managers::

    >>> resp = moderator.options(document_item).json
    >>> 'adhocracy_core.sheets.metadata.IMetadata' \
    ...     in resp['PUT']['request_body']['data']
    True

Note: normally the sheets listed in the OPTIONS response are just mapped to
empty dictionaries, the contained fields are not listed. But IMetadata is a
special case since not everybody who can delete a resource can hide it.
Therefore, the presence of the 'deleted' and/or 'hidden' fields indicates
that PUTting a new value for this field is allowed. Once more, the
corresponding value is just a stub (the empty string) and doesn't have any
meaning.

Lets hide pool2::

    >>> data = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...         'data': {'adhocracy_core.sheets.metadata.IMetadata':
    ...                      {'hidden': True}}}
    >>> resp = admin.put('/pool2', data).json

Inspecting the 'updated_resources' listing in the response, we see that
pool2 was removed::

    >>> resp['updated_resources']['removed']
    ['.../pool2/']

Now we get an error message when trying to retrieve the pool2::

    >>> resp = anonymous.get('/pool2')
    >>> resp.status_code
    410
    >>> resp.json['reason']
    'hidden'
    >>> resp.json['modified_by']
    '.../principals/users/000...'
    >>> 'modification_date' in resp.json
    True

Nested resources inherit the hidden flag from their ancestors. Hence
the child of the pool2 is now hidden too::

    >>> resp = anonymous.get('/pool2/child')
    >>> resp.status_code
    410
    >>> resp.json['reason']
    'hidden'

Only the pool1 is still visible in the pool::

    >>> resp = anonymous.get('/', params={'elements': 'paths'}).json
    >>> rest_url + '/pool1/' in resp['data']['adhocracy_core.sheets.pool.IPool']['elements']
    True
    >>> rest_url + '/pool2/' in resp['data']['adhocracy_core.sheets.pool.IPool']['elements']
    False

Sanity check: internally, the backend uses a *private_visibility* index to keep
track of the visibility/deletion status of resources. But this filter is
private and cannot be directly queried from the frontend::

    >>> resp = anonymous.get('/', {'private_visibility': 'hidden'})
    >>> resp.status_code
    400
    >>> resp.json['errors'][0]['description']
    'Unrecognized keys in mapping: "{\'private_visibility\': \'hidden\'}"'

Lets hide an item with referenced resources. Prior to doing so, lets check
that there actually is a listed version::

    >>> resp = anonymous.get(document_item)
    >>> document_creator == resp.json['data']['adhocracy_core.sheets.metadata.IMetadata']['creator']
    True

Now we hide the item::

    >>> data = {'content_type': 'adhocracy_core.resources.document.IDocumentItem',
    ...         'data': {'adhocracy_core.sheets.metadata.IMetadata':
    ...                      {'hidden': True}}}
    >>> resp = moderator.put(document_item, data)
    >>> resp.status
    '200 OK'

The referenced user resource is affected by this change since its
back references have changed. Therefore, it shows up in the list of modified
resources::

    >>> document_creator in resp.json['updated_resources']['modified']
    True

In the end we can cleanup with some real deletion::

    >>> resp = admin.delete("/pool1")
    >>> resp.status_code
    200

    >>> resp.json['updated_resources']['removed']
    ['.../pool1...

    >>> resp = admin.get("/pool1")
    >>> resp.status_code
    404
