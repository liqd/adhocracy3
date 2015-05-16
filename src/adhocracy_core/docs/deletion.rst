Deleting and Hiding Resources
=============================

Two boolean fields (flags) defined in the
*adhocracy_core.sheets.metadata.IMetadata* sheet can be used to delete or
hide resources: *deleted* and *hidden*. Both default to false. If this sheet
is omitted when POSTing new resources, the default values are used.

Deleting or hiding an existing resource is only possible for updatable
resources, i.e. *not* for Versions (which are immutable and hence don't
allow PUT).

Anyone who can edit a resource (editor role) can *delete* it by PUTting an
update with *IMetadata { deleted: true }*. Likewise they can undelete a
deleted resource by PUTting an update with *IMetadata { deleted: false
}*. For simplicity, our PUT works like the HTTP PATCH command (added in RFC
5789): any sheet and fields not mentioned in the PUTted data structure are
left unchanged.

Anyone with the *hide_resource* permission (typically granted to the manager
role) can *hide* a resource by PUTting an update with *IMetadata { hidden:
true }*. Likewise they can un-hide a hidden resource by PUTting an update with
*IMetadata { hidden: false }*. Nobody else can change the value of the
*hidden* field.

Newly created resources can also be marked as *deleted* or *hidden* by
setting the initial value of these flags accordingly. However,
the same permission restrictions apply. This might be useful for creating a
*deleted* version as a successor of another version to mark the preceding
version as obsolete. POSTing a resource with *IMetadata { hidden: true }*
requires the *hide_resource* permission and, frankly, doesn't make any sense.

The effect of these flags is as follows:

* A positive value of the *deleted* and *hidden* flags is inherited by
  child/descendant resources (whose resource path includes the path of the
  deleted/hidden ancestor as prefix). Hence a *deleted* resource is one
  that has its own *deleted* flag set to true or that has an ancestor whose
  *deleted* flag is true. Likewise for *hidden* resources.
* Normally, only resources that are neither *deleted* nor *hidden* are
  listed in parent pools and search queries.
* FIXME Not implemented yet, since the frontend doesn't yet need it:
  The parameter *include=deleted|hidden|all* can be used to include
  deleted and/or hidden resources in pool listings and other search queries.
  If its value is *deleted*, resources will be found regardless of the value
  of their *deleted* flag, but only if they are not *hidden.* If its value is
  *hidden*, resources will be found regardless of the value of their *hidden*
  flag, but only if they are not *deleted.* If its value is *all*, all
  resources will be found. Anyone can specify these flags and get the paths
  of deleted and/or hidden resources. However, only those with *hide_resource*
  permission are ever able to view the contents of hidden resources.
  It's also possible to set *include=visible* to get only non-deleted and
  non-hidden resources, but it's not necessary since that is the default.
* If the frontend attempts to retrieve a *deleted* or *hidden* resource via
  GET, the backend normally responds with HTTP status code *410 Gone*.
  FIXME Not implemented yet, since the frontend doesn't yet need it:
  The frontend can override this by adding the parameter
  *include=deleted|hidden|all* to the GET request, just as in search queries.
  Anybody can view deleted resources in this way, and managers (those with
  *hide_resource* permission) can view hidden resources in these ways. Those
  without this permission will still get a *410 Gone* if the resource is
  hidden.
* The body of the *410 Gone* is a small JSON document that explains why the
  resource is gone (whether it was deleted or hidden). It also shows who
  made the last change to the resource and when::

      { "reason": "deleted|hidden|both",
        "modified_by:" "<path-to-user>",
        "modification_date": "<timestamp>"}

  Often the last modification will have been the deletion or hiding of
  the resource, but there is no guarantee that this is always the case.
  Especially, the resource may be marked as hidden/deleted because one of its
  ancestors was hidden/deleted (as that status is inherited). In that case,
  the person who last modified the child resource likely has nothing to do
  with the person who hid/deleted the ancestor resource.
* *Deleted* or *hidden* resources may still be referenced from other
  resources. If the frontend follows such references it must therefore
  be prepared to encounter *410 Gone* responses and deal with them
  appropriately (e.g. by silently skipping them or by showing an
  explanation such as "Comment deleted").
* FIXME Not implemented yet, since the frontend doesn't yet need it.
  *Deleted* and *hidden* resources will normally not be shown in
  backreferences, which are calculated on demand. The
  *include=deleted|hidden|all* parameter can be used to change that and
  include backreferences to deleted and/or hidden resources. The same
  restrictions apply, i.e. normal users can use this parameter to find out
  whether hidden backreferences exist, but they won't be able to see their
  contents. In any case the frontend should be prepared to deal with
  *410 Gone* when following backreferences in the same way as when
  following forward reference -- even if it didn't explicitly ask to include
  them, they might show up due to caching.

FIXME We should extend the Meta API to expose the distinction between
references and backreferences to the frontend, currently only the backend
knows this.

Notes:

* Physical deletion of resources (pruning them from the DB without hope of
  resurrection) is not currently possible through the REST API. There may be
  server-side processes that prune some specific or even all *hidden*
  resources from the DB from time to time or when started by an admin, but
  they cannot be controlled via REST and are not specified or documented
  here.
* The HTTP DELETE command is not used since it would imply physically
  deleting a resource.
* This document is about deletion of resources (JSON documents). Deletion
  of uploaded assets (images, PDFs etc.) is outside its current scope.
* Currently, the deleted/hidden status of resources isn't treated as special
  by the Websocket server. So, if an resource is flagged as deleted/hidden
  (or undeleted etc.), a "modified" event is sent to subscribers of that
  resource and a "modified_child" event is sent to subscribers of the parent
  pool. FIXME At same point in the future, we might want to change that and
  send "removed"/"removed_item" messages instead.


A Censorship Example
--------------------

Lets put the above theory into practice by hiding (censoring) some content!

Some imports to work with rest api calls::

    >>> from pprint import pprint

Start adhocracy app and log in some users::

    >>> anonymous = getfixture('app_anonymous')
    >>> participant = getfixture('app_participant')
    >>> moderator = getfixture('app_moderator')
    >>> admin = getfixture('app_admin')

Lets create some content::

    >>> data = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name':  'pool2'}}}
    >>> resp = admin.post("/", data)
    >>> data = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'child'}}}
    >>> resp = admin.post("/pool2", data)
    >>> data = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'pool1'}}}
    >>> resp = admin.post("/", data)
    >>> data = {'content_type': 'adhocracy_core.resources.sample_proposal.IProposal',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'proposal_item'}}}
    >>> resp = participant.post("/pool1", data)
    >>> proposal_item = resp.json['path']
    >>> proposal_item_first_version = resp.json['first_version_path']

    >>> data = {'content_type': 'adhocracy_core.resources.sample_section.ISection',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'section_item'},}
    ...         }
    >>> resp = participant.post(proposal_item, data)
    >>> section_item = resp.json["path"]
    >>> section_item_first_version = resp.json["first_version_path"]
    >>> data = {'content_type': 'adhocracy_core.resources.sample_paragraph.IParagraph',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'paragraph_item'},}
    ...         }
    >>> resp = participant.post(proposal_item, data)
    >>> paragraph_item = resp.json["path"]
    >>> paragraph_item_first_version = resp.json["first_version_path"]
    >>> data = {'content_type': 'adhocracy_core.resources.sample_section.ISectionVersion',
    ...         'data': {
    ...              'adhocracy_core.sheets.document.ISection': {
    ...                  'elements': [paragraph_item_first_version]},
    ...               'adhocracy_core.sheets.versions.IVersionable': {
    ...                  'follows': [section_item_first_version]
    ...                  }
    ...          },
    ...         }
    >>> resp = participant.post(section_item, data)
    >>> section_item_second_version = resp.json["path"]

As expected, we can retrieve the pool and its child::

    >>> resp = anonymous.get("/pool2").json
    >>> 'data' in resp
    True
    >>> resp = anonymous.get("/pool2/child").json
    >>> 'data' in resp
    True

Both pools show up in the pool sheet::

    >>> resp = anonymous.get("/").json
    >>> pprint(sorted(resp['data']['adhocracy_core.sheets.pool.IPool']
    ...                        ['elements']))
    ['.../adhocracy/pool1/', '.../adhocracy/pool2/']

Lets check whether we have the permission to delete or hide resources.
The person who has created a resource (creator role) has the right to delete
it::

    >>> resp = anonymous.get("/pool1/proposal_item").json

    >>> resp = participant.options("/pool1/proposal_item").json
    >>> resp['PUT']['request_body']['data']['adhocracy_core.sheets.metadata.IMetadata']
    {'deleted': [True, False]}

But they cannot hide it -- that special right is reserved to managers::

    >>> resp = moderator.options("/pool1/proposal_item").json
    >>> pprint(resp['PUT']['request_body']['data']['adhocracy_core.sheets.metadata.IMetadata'])
    {'deleted': [True, False], 'hidden': [True, False]}

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
    >>> resp = moderator.put("/pool2", data).json

Inspecting the 'updated_resources' listing in the response, we see that
pool2 was removed::

    >>> resp['updated_resources']['removed']
    ['http://localhost/adhocracy/pool2/']

Now we get an error message when trying to retrieve the pool2::

    >>> resp = anonymous.get("/pool2")
    >>> resp.status_code
    410
    >>> resp.json['reason']
    'hidden'
    >>> resp.json['modified_by']
    '.../principals/users/000...'
    >>> 'modification_date' in resp.json
    True

Nested resources inherit the deleted/hidden flag from their ancestors. Hence
the child of the pool2 is now hidden too::

    >>> resp = anonymous.get("/pool2/child")
    >>> resp.status_code
    410
    >>> resp.json['reason']
    'hidden'

Only the pool1 is still visible in the pool::

    >>> resp = anonymous.get("/").json
    >>> resp['data']['adhocracy_core.sheets.pool.IPool']['elements']
    ['.../adhocracy/pool1/']

Sanity check: internally, the backend uses a *private_visibility* index to keep
track of the visibility/deletion status of resources. But this filter is
private and cannot be directly queried from the frontend::

    >>> resp = anonymous.get("/", {'private_visibility': 'hidden'})
    >>> resp.status_code
    400
    >>> resp.json['errors'][0]['description']
    'No such catalog'

Lets hide an item with referenced item versions. Prior to doing so, lets check
that there actually is a listed version::

    >>> resp = anonymous.get(paragraph_item_first_version)
    >>> resp.json['data']['adhocracy_core.sheets.document.IParagraph']['elements_backrefs']
    ['http://localhost/adhocracy/pool1/proposal_item/section_item/VERSION_0000001/']

Now we hide the item::

    >>> data = {'content_type': 'adhocracy_core.resources.sample_proposal.IProposalItem',
    ...         'data': {'adhocracy_core.sheets.metadata.IMetadata':
    ...                      {'hidden': True}}}
    >>> resp = moderator.put(section_item, data)
    >>> resp.status
    '200 OK'

The paragraph version that was referenced from the now hidden section version
is affected by this change since its backreferences have changed. Therefore,
it shows up in the list of modified resources::

    >>> paragraph_item_first_version in resp.json['updated_resources']['modified']
    True

Now the hidden item versions are removed from backreference listings:

    >>> resp = anonymous.get(paragraph_item_first_version)
    >>> resp.json['data']['adhocracy_core.sheets.document.IParagraph']['elements_backrefs']
    []
