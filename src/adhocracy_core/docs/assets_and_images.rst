Assets and Images
=================

FIXME All of this still needs to be implemented. This document will be
revised and turned into a doctest along with the implementation.

*Assets* are files of arbitrary type that can be uploaded to and downloaded
from the backend. From the viewpoint of the backend, they are just "blobs"
-- binary objects without any specific semantic.

*Images* are a subtype of assets; they an be resized and cropped to
different target formats.

To manage assets, the backend has the `adhocracy_core.resources.asset.IAsset`
resource type, which is a special kind of *Pool.* (FIXME Or possibly it's a
*Simple*? In any case, it's not versionable.)

Assets can be uploaded to an *asset post pool,* which is a kind of post pool
(just as there are post pools for comments and rates). A resource that
allows asset upload provides the
`adhocracy_core.sheets.asset.IAssetContainer` sheet (just like
commentable resources provide the `adhocracy_core.sheets.comment.ICommentable`
sheet).

`IAssetContainer`s have two fields:

:post_pool: path to the asset post pool where assets can be posted
:assets: a list of assets that have already been attached to the resource
    -- this is a read-only list of backreferences which is automatically
   populated by the backend (like the `comments` field in `ICommentable`)

The `adhocracy_core.resources.asset.IAsset` resource type provides two sheets,
`adhocracy_core.sheets.metadata.IMetadata` and
`adhocracy_core.sheets.asset.IAsset`.

The `adhocracy_core.sheets.metadata.IMetadata` sheet is automatically created
and updated by the backend. The `adhocracy_core.sheets.asset.IAsset` sheet
has two fields that must be set by the frontend when posting a new asset:

:mime_type: the MIME type of the asset
:attached_to: the path of the resource to which the asset belongs, which must
    provide the `adhocracy_core.sheets.asset.IAssetContainer` sheet (like
    the `refers_to` field in `IComment`)

Asset Subtypes and MIME Type Validators
---------------------------------------

Note: this section is mostly backend-specific.

The generic `adhocracy_core.resources.asset.IAsset` resource type allows
uploading resources of arbitrary MIME types. To allow uploading only files
of specific types, subclass it and register a
`adhocracy_core.interfaces.IMimeTypeValidator` implementation for that
subtype (same as with `IRateValidator` for rates).

E.g. to create a spreadsheet asset type that only accepts OpenDocument and
Excel spreadsheets::

    class ISpreadsheetAsset(IAsset):
        """Empty marker interface for spreadsheet assets."""

    @implementer(IMimeTypeValidator)
    class SpreadsheetMimeTypeValidator:

        def validate(self, mime_type: str) -> bool:
            return mime_type in (
                'application/vnd.oasis.opendocument.spreadsheet',
                'application/vnd.ms-excel')

    config.registry.registerAdapter(SpreadsheetMimeTypeValidator,
                                    (ISpreadsheetAsset,),
                                    IMimeTypeValidator)

Images and Size Mappers
-----------------------

Note: this section is mostly backend-specific.

A predefined IAsset subtype is `adhocracy_core.resources.asset.IImage`. Its
adapter allows MIME types that start with 'image/', i.e.,
arbitrary image files (subtypes of IImage can restrict that further,
if desired).

The backend can resize and crop images to different target formats. To do
this, define an IImage subtype and register a
`adhocracy_core.interfaces.ImageSizeMapper` implementation for that
subtype::

    class IProposalIntroImage(IImage):
        """Empty marker interface."""

    @implementer(ImageSizeMapper)
    class IProposalIntroImageSizeMapper:

        def sizemap -> dict:
            return {
                'thumbnail': Dimensions(width=160, height=120),
                'detail': Dimensions(width=600, height=300),
            }

    # register adapter as above

This means that the image will be made available in 'thumbnail' and in
'detail' size, each with the specified dimensions, as well as in its original
(raw) size.

The image will be automatically resized to all of the specified sizes. If
the target aspect ratio is different from the original aspect ratio, the size
that is wider/higher is cropped so that only the middle part of it remains.
For example, if the original image has 1600x600 pixel and the target size is
600x300 ('detail' size in the above example), it will be scaled to 50%
(800x300 pixel) and then 100 pixel to the left and 100 to the right will be
cropped to reach the target size.

Uploading Assets
----------------

To upload assets, the frontend sends a POST request with
enctype="multipart/form-data" to an asset post pool. The request must have
the following fields:

:content_type: the type of the resource that shall be created, e.g.
    "adhocracy_core.resources.sample_proposal.IProposalIntroImage"
:mime_type: the MIME type of the uploaded file, e.g. "image/jpeg"
:attached_to: the path of the resource to which the asset belongs
:asset: the binary data of the uploaded file, as per the HTML
    `<input type="file" name="asset">` tag.

FIXME Alternatively, the frontend could upload *two* files: (1) the binary
data of the uploaded file and (2) a small JSON document containing the
content type of the resource and the values of the
`adhocracy_core.sheets.asset.IAsset` in our usual way. Would that be easier
for the frontend and/or the backend??

In response, the backend sends a JSON document with the resource type and
path of the new resource (just as with other resource types)::

    {"content_type": "adhocracy_core.resources.sample_proposal.IProposalIntroImage",
     "path": "http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000"}

FIXME It should be possible to restrict the types of assets that can be
posted to a specific asset post pool; e.g. an asset post pool might only
accept IProposalIntroImages and/or ISpreadsheetAssets,
but no other asset types. What's the best way to do that?

Downloading Assets
------------------

Assets can be downloaded in different ways:

  * As a JSON document containing just the metadata
  * As raw document containing the uploaded "blob"
  * In case of images, in one of the cropped sizes defined by the
    ImageSizeMapper

The frontend can retrieve the JSON metadata by GETting the resource path of
the asset::

    >> resp_data = testapp.get(
    ...    'http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000').json
    >> pprint(resp_data)
    {'content_type': 'adhocracy_core.resources.sample_proposal.IProposalIntroImage',
     'data': {
         'adhocracy_core.sheets.metadata.IMetadata': {
             'creation_date': '...',
             'creator': '...',
             'deleted': 'false',
             'hidden': 'false',
             'modification_date': '...',
             'modified_by': '...'},
         'adhocracy_core.sheets.asset.IAsset': {
             'attached_to': 'http://localhost/adhocracy/proposals/myfirstproposal/VERSION_0000001',
             'mime_type': 'image/jpeg'}},
     'path': '"http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000"'}

FIXME If that information is important/useful for the frontend, it might
also be possible to have a read-only `adhocracy_core.sheets.asset.IImage`
sheet that lists the sizes supported by the ImageSizeMapper::

    "adhocracy_core.sheets.asset.IImage": {
        "sizes": {
            "thumbnail": "160x120",
            "detail": "600x300"
        }
    }

It can retrieve the raw uploaded data by GETting its `raw` child::

    >> resp_data = testapp.get(
    ...    'http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000/raw').json
    >> resp_data["content_type"]
    'image/jpeg'

In case of images, it can retrieve the image in one of the predefined
cropped sizes by asking for one of the keys defined by the ImageSizeMapper as
child element::

    >> resp_data = testapp.get(
    ...    'http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000/thumbnail').json
    >> resp_data["content_type"]
    'image/jpeg'

Replacing an Asset
------------------

To upload a new version of an asset, the frontend can sent a PUT request with
enctype="multipart/form-data" to the asset URL. The PUT request *must* contain
an `asset` field with the binary data of the new upload. It *may* contain the
other fields used when POSTing new assets -- they can be omitted if their value
hasn't changed.

Only those who have *editor* rights for an asset can PUT a replacement asset.
If an image is replaced, all its cropped sizes will be automatically be
updated as well.

Since assets aren't versioned, the old binary "blob" will be physically and
irreversibly discarded once a replacement blob is uploaded.

Deleting and Hiding Assets
--------------------------

Assets can be deleted or censored ("hidden") in the usual way, see
:ref:`deletion`. In contrast to deletion or hiding of normal resource,
asset deletion/hiding will however physically discard the binary "blob",
so it's not really reversible.

It is possible to undelete or unhide a deleted/hidden asset,
but the "raw" view and any alternative sizes defined for images will be empty
until a replacement blob is uploaded.

Asset Containers and Asset Filtering
------------------------------------

The `assets` field of an `adhocracy_core.sheets.asset.IAssetContainer` will
list *all* the assets *attached_to* that resource, regardless of their type.
If multiple asset types belong to a resource, the frontend can query its
asset post pool to retrieve just assets of a specific type (see the
"Filtering Pools" section in :ref:`rest_api`)::

    >> resp_data = testapp.get('http://localhost/adhocracy/proposals/myfirstproposal/assets',
    ...     params={'content_type': 'adhocracy_core.resources.sample_proposal.IProposalIntroImage',
    ...             'adhocracy_core.sheets.asset.IAsset:attached_to':
    ...             'http://localhost/adhocracy/proposals/myfirstproposal/VERSION_0000001'
    ...             }).json
    >> pprint(resp_data['data']['adhocracy_core.sheets.pool.IPool']['elements'])
    ['http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000']
