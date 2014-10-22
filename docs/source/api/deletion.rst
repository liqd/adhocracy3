Deleting and Hiding Resources
=============================

All resources that can be deleted implement the *Deletable* sheet.
Typically all Simples and all Items can be deleted and hence implement this
sheet. Versions typically won't be deletable (since they are immutable) and
hence don't implement this sheet.

The *Deletable* sheet has two boolean fields (flags): *deleted* and
*hidden*. Both default to false. For simplicity, the sheet may be omitted
when POSTing new resources -- in this case, the default values will be
used.

Anyone who can edit a resource (editor role) can *delete* it by PUTting an
update with *Deletable { deleted: true }*. Likewise they can undelete a
deleted resource by PUTting a new version with *Deletable { deleted: false
}*. For simplicity, our PUT works like the HTTP PATCH command (added in RFC
5789): any sheet and fields not mentioned in the PUTted data structure are
left unchanged.

Anyone with the manager role can *hide* a resource by PUTting an update
with *Deletable { hidden: true }*. Likewise they can un-hide a hidden
resource by PUTting a new version with *Deletable { hidden: false }*.
Nobody else can change the value of the *hidden* field.

The effect of these flags is as follows:

* A positive value of the *deleted* and *hidden* flags is inherited by
  child/descendant resources (whose resource path includes the path of the
  deleted/hidden ancestor as prefix). Hence a *deleted* resource is one
  that has its own *deleted* flag set to true or that has an ancestor whose
  *deleted* flag is true. Likewise for *hidden* resources.
* Only resources that are neither *deleted* nor *hidden* are listed in
  parent pools.
* Only resources that are neither *deleted* nor *hidden* show up in normal
  search queries.
* The search parameter *show=deleted|hidden|all* can be used to include
  deleted and/or hidden resources in search queries. If its value is
  *deleted*, resources will be found regardless of the value of their
  *deleted* flag, but only if they are not *hidden.* Anyone can do this. If
  its value is *hidden*, resources will be found regardless of the value of
  their *hidden* flag, but only if they are not *deleted.* Only managers
  can do this. If its value is *all*, all resources will be found. Only
  managers can do this. If a non-manager searches with *show=hidden|all*, the
  backend responds with an error.
* If the frontend attempts to retrieve a *deleted* or *hidden* resource via
  GET, the backend normally responds with HTTP status code *410 Gone*. The
  frontend can override this by adding the parameter
  *show=deleted|hidden|all* to the GET request, just as in search queries.
  The same restriction applies, i.e. anybody can specify *show=deleted* (and
  then retrieve the resource if it was merely deleted), but only managers
  can specify *show=hidden|all* (and then retrieve the resource if it was
  hidden).
* FIXME Should the *410 Gone* response have a JSON body explaining the
  reason: `{ 'reason': 'deleted|hidden|both' }` ?
* *Deleted* or *hidden* resources may still by referenced from other
  resources. If the frontend follows such references it must therefore
  be proposed to encounter *410 Gone* responses and deal with them
  appropriately (e.g. by silently skipping them or by showing an
  explanation such as "Comment deleted").
* *Deleted* and *hidden* resources will *normally* not be shown in
  backreferences, which are calculated on demand. However, due to caching,
  they may still show up, so the frontend should be prepared to deal with
  *410 Gone* when following backreferences in the same way as when
  following forward reference.

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
