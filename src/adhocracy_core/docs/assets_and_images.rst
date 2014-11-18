Assets and Images
=================

Introduction
------------

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

Assets can be uploaded to an *asset pool.* Resources that provide an asset
pool implement the `adhocracy_core.sheets.asset.IHasAssetPool` sheet, which
has a single field:

:asset_pool: path to the asset pool where assets can be posted

The `adhocracy_core.resources.asset.IAsset` resource type provides three
sheets:

* `adhocracy_core.sheets.metadata.IMetadata`: provided by all resources,
  automatically created and updated by the backend
* `adhocracy_core.sheets.asset.IAssetMetadata` with the fields:

  :mime_type: the MIME type of the asset; must be specified by the frontend,
      but the backend will sanity-check the posted data and reject the asset
      in case of an detectable mismatch (e.g. if the frontend posts a Word file
      but gives "image/jpeg" as MIME type). Not all mismatches will be
      detectable, e.g. different "text/" subtypes can be hard to distinguish.
  :size: the size of the asset (in bytes)
  :filename: the name of the file uploaded by the frontend (in the backend,
      the asset will have a different, auto-generated path)
  :attached_to: a list of backreferences pointing to resources that refer
      to the asset; this attribute is read-only and managed by the backend

* `adhocracy_core.sheets.asset.IAssetData` with a single field:

  :data: the binary data of the asset ("blob")

  This sheet is POST/PUT-only, see below on how to download/view the binary
  data.

Asset Subtypes and MIME Type Validators
---------------------------------------

Note: this section is mostly backend-specific.

The generic `adhocracy_core.sheets.asset.IAssetMetadata` sheet doesn't limit
the MIME type of assets. Since this is rarely desirable, it is considered
abstract and cannot be instantiated -- only subclasses that provide a *MIME
Type Validator* can. To do so, create a subclass of the sheet (empty marker
interface) and register a `adhocracy_core.interfaces.IMimeTypeValidator`
implementation for that subclass (same as with `IRateValidator` for rates).

E.g. to create a spreadsheet asset type that only accepts OpenDocument and
Excel spreadsheets::

    class ISpreadsheetAsset(IAssetMetadata):
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

FIXME Maybe we'll extend the SheetMetadata instead of using an adapter
(likewise for Size Mappers).

Images and Size Mappers
-----------------------

Note: this section is mostly backend-specific.

A predefined IAssetMetadata subtype is
`adhocracy_core.resources.asset.IImageMetadata`. Its adapter allows MIME
types that start with 'image/', i.e., arbitrary image files (subtypes of
IImage can restrict that further, if desired).

The backend can resize and crop images to different target formats. To do
this, define an IImageMetadata subtype and register a
`adhocracy_core.interfaces.ImageSizeMapper` implementation for that
subtype::

    class IProposalIntroImage(IImageMetadata):
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

Assets are uploaded (POST) and updated (PUT) in a special way. Instead of
sending a JSON document, the field names and values are flattened into
key/value pairs that are sent as a "multipart/form-data" request. Hence, the
request will typically have the following keys:

:content_type: the type of the resource that shall be created, e.g.
    "adhocracy_core.resources.sample_proposal.IProposalIntroImage"
:data.adhocracy_core.sheets.asset.IAssetMetadata.mime_type: the MIME type of
    the uploaded file, e.g. "image/jpeg"
:data.adhocracy_core.sheets.asset.IAssetMetadata.size: the size of the file
:data.adhocracy_core.sheets.asset.IAssetMetadata.filename: the original name
    of the file
:data.adhocracy_core.sheets.asset.IAssetData.data: the binary data of the
    uploaded file, as per the HTML `<input type="file" name="asset">` tag.

In response, the backend sends a JSON document with the resource type and
path of the new resource (just as with other resource types)::

    {"content_type": "adhocracy_core.resources.sample_proposal.IProposalIntroImage",
     "path": "http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000"}

Updating Assets
---------------

To upload a new version of an asset, the frontend sends a PUT request with
enctype="multipart/form-data" to the asset URL. The PUT request may contain
the same keys as a POST request used to create a new asset,
but all of them are optional -- if a field isn't change by the update,
there is no need to include the key.

If the `content_type` key is given, is *must* be identical to the current
content type of the asset (changing the type of resources is generally not
allowed).

Typically, the PUT request will be used to replace the binary data of the
asset, hence it will contain the
`data.adhocracy_core.sheets.asset.IAssetData.data` key. But it's also
allowed to omit that key and only change the
`data.adhocracy_core.sheets.asset.IAssetMetadata.filename`, for example.

Only those who have *editor* rights for an asset can PUT a replacement asset.
If an image is replaced, all its cropped sizes will be automatically
updated as well.

Since assets aren't versioned, the old binary "blob" will be physically and
irreversibly discarded once a replacement blob is uploaded.

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
         'adhocracy_core.sheets.asset.IAssetMetadata': {
             'attached_to': [
                 'http://localhost/adhocracy/proposals/myfirstproposal/VERSION_0000001'
              ],
             'mime_type': 'image/jpeg'},
             'filename': 'greatpicture.jpg',
             'size': '1906117'},
     'path': '"http://localhost/adhocracy/proposals/myfirstproposal/assets/0000000"'}

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

Deleting and Hiding Assets
--------------------------

Assets can be deleted or censored ("hidden") in the usual way, see
:ref:`deletion`. In contrast to deletion or hiding of normal resource,
asset deletion/hiding will however physically discard the binary "blob",
so it's not really reversible.

It is possible to undelete or unhide a deleted/hidden asset,
but the "raw" view and any alternative sizes defined for images will be empty
until a replacement blob is uploaded.

FIXME Settle with product owner whether this is the desired behavior.

Referring to Assets
-------------------

Sheets can have fields that refer to assets of a specific type. This is done
in the usual way be setting the type of the field to `Reference` (to refer
to a single asset) or `UniqueReferences` (to refer to a list of assets) and
defining a suitable `reftype` (e.g. with `target_isheet =
IProposalIntroImage`).
