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

Anyone with the *canhide* permission (typically granted to the manager role)
can *hide* a resource by PUTting an update with *IMetadata { hidden: true }*.
Likewise they can un-hide a hidden resource by PUTting an update with
*IMetadata { hidden: false }*. Nobody else can change the value of the
*hidden* field.

Newly created resources can also be marked as *deleted* or *hidden* by
setting the initial value of these flags accordingly. However,
the same permission restrictions apply. This might be useful for creating a
*deleted* version as a successor of another version to mark the preceding
version as obsolete. POSTing a resource with *IMetadata { hidden: true }*
requires the *canhide* permission and, frankly, doesn't make any sense.

The effect of these flags is as follows:

* A positive value of the *deleted* and *hidden* flags is inherited by
  child/descendant resources (whose resource path includes the path of the
  deleted/hidden ancestor as prefix). Hence a *deleted* resource is one
  that has its own *deleted* flag set to true or that has an ancestor whose
  *deleted* flag is true. Likewise for *hidden* resources.
* Normally, only resources that are neither *deleted* nor *hidden* are
  listed in parent pools and  search queries.
* The parameter *include=deleted|hidden|all* can be used to include
  deleted and/or hidden resources in pool listings and other search queries.
  If its value is *deleted*, resources will be found regardless of the value
  of their *deleted* flag, but only if they are not *hidden.* If its value is
  *hidden*, resources will be found regardless of the value of their *hidden*
  flag, but only if they are not *deleted.* If its value is *all*, all
  resources will be found. Anyone can specify these flags and get the paths
  of deleted and/or hidden resources. However, only those with *canhide*
  permission are ever able to view the contents of hidden resources.
* If the frontend attempts to retrieve a *deleted* or *hidden* resource via
  GET, the backend normally responds with HTTP status code *410 Gone*. The
  frontend can override this by adding the parameter
  *include=deleted|hidden|all* to the GET request, just as in search queries.
  Anybody can view deleted resources in this way, and managers (those with
  *canhide* permission) can view hidden resources in these ways. Those
  without this permission will still get a *410 Gone* if the resource is
  hidden.
* The body of the *410 Gone* is a small JSON document that explains why the
  resource is gone (whether it was deleted or hidden). It also shows who
  made the last change to the resource and when::

      { "reason": "deleted|hidden|both",
        "modified_by:" "<path-to-user>",
        "modification_date": "<timestamp>"}

  Typically the last modification will have been the deletion or hiding of
  the resource, but there is no guarantee that this is always the case.
* *Deleted* or *hidden* resources may still be referenced from other
  resources. If the frontend follows such references it must therefore
  be proposed to encounter *410 Gone* responses and deal with them
  appropriately (e.g. by silently skipping them or by showing an
  explanation such as "Comment deleted").
* *Deleted* and *hidden* resources will normally not be shown in
  backreferences, which are calculated on demand. The
  *include=deleted|hidden|all* parameter can be used to change that and
  include backreferences to deleted and/or hidden resources. The same
  restrictions apply, i.e. normal users can use this parameter to find out
  whether hidden backreferences exist, but they won't be able to see their
  contents. In any case the frontend should be prepared to deal with
  *410 Gone* when following backreferences in the same way as when
  following forward reference -- even if it didn't explicitly ask to include
  them, they might show up to due caching.

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
* This proposal is about deletion of resources (JSON documents). Deletion
  of uploaded assets (images, PDFs etc.) is outside the scope of this
  proposal and will be dealt with (if needed) in the File Upload story.
