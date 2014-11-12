File and Image Upload
=====================

FIXME All of this still needs to be implemented. This document will be
revised and made testable along with the implementation.

*Assets* are files of arbitrary type that can be uploaded to and downloaded
from the backend. From the viewpoints of the backend, they are just "blobs"
-- binary objects without any specific semantic.

*Images* are a subtype of assets; they an be resized and cropped to
different target formats.

To manage assets, the backend has the `adhocracy_core.resources.asset.IAsset`
resource type, which is a special kind of *Pool.* (FIXME Or maybe it's a
*Simple*? In any case, it's not versionable.)

Assets can be uploaded to an *asset post pool,* which is a kind of post poll
(just as there are post pools for comments and rates). A resource that
allows asset upload provides the
`adhocracy_core.sheets.asset.IAssetContainer` sheet (just like
commentable resources provide the `adhocracy_core.sheets.comment.ICommentable`
sheet).

`AssetContainer`s has two fields:

* `post_pool`: path to the asset post pool where assets can be posted
* `assets`: a list of assets that have already been attached to the resource
 -- this is a readonly list of backreferences which is automatically populated
 by the backend (like the `comments` field in `ICommentable`s)

The `adhocracy_core.resources.asset.IAsset` resource type provides two sheets,
`adhocracy_core.sheets.metadata.IMetadata` and either
`adhocracy_core.sheets.asset.IAsset`.

The `IMetadata` is automatically created and updated by the backend.
The `adhocracy_core.sheets.asset.IAsset` sheet has just one field that must be
set by the frontend when posting a new asset: the `mime_type` of the asset.I

Asset Subtypes and MIME Type Validators
---------------------------------------

Note: this section is mostly backend-specific.

The generic `adhocracy_core.resources.asset.IAsset` resource type allows
uploading resources of an arbitrary MIME type. To allow uploading only files
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
as desired).

The backend can resize and crop images to different target formats. To do
this, define a IImage subtype and register a
`adhocracy_core.interfaces.ImageSizeMapper` implementation for that
subtype::

    class ProposalIntroImage(IImage):
        """Empty marker interface."""

    @implementer(ImageSizeMapper)
    class ProposalIntroImageSizeMapper:

        def sizemap -> dict:
            return {
                'thumbnail': Dimensions(width=160, height=120),
                'detail': Dimensions(width=600, height=300),
            }

    # register adapter as above

This means that the image will be made available in 'thumbnail' and in
'detail' size, each with the specified dimensions,
as well as in its original (raw) size.


Uploading Assets
----------------

To upload assets, the frontend sends a "multipart/form-data" POST request to
an asset post pool. TODO asset, mime_type, content_type.

Defining File and Image Nodes in Sheets
---------------------------------------

This section is about schema definitions in the backend, it doesn't directly
concern the REST API.

Sheets can include references to uploaded files defining fields of the type
`adhocracy_core.schema.File` or `adhocracy_core.schema.Image`.

`adhocracy_core.schema.File` is a Colander schema node with an optional
`mime_type` attribute that specifies a list of accepted MIME types. For
example, a File node names *business_plan* that accepts OpenDocument and Excel
spreadsheets::

    business_plan = adhocracy_core.schema.File(mime_type=[
                       'application/vnd.oasis.opendocument.spreadsheet',
                       'application/vnd.ms-excel'])

If no `mime_type` is specified, files of arbitrary type are allowed.
If a `mime_type` ends with `/`, all MIME types that start with that prefix
are allowed. E.g. to allow uploading an arbitrary audio file::

    sound_sample = adhocracy_core.schema.File(mime_type=['audio/'])

`adhocracy_core.schema.Image` is a subtype of `adhocracy_core.schema.File`
that handles automatic cropping and resizing of images. It supports an
additional `sizes` attribute that specifies a list of target sizes.
Each element must be an `adhocracy_core.schema.ImageSize`. This class has
three required constructor arguments: `name`, `width`, `height`. Each name
should only be used once per list; the name *original* is reserved and
shouldn't be used at all.

For example, we can define a field *picture* that accepts JPEG and PNG
images and specifies two target sizes::

    from adhocracy_core.schema import Image, ImageSize
    picture = Image(mime_type=['image/jpeg', 'image/png'],
                    sizes=[
                        ImageSize(name='thumbnail', width=160, height=120)
                        ImageSize(name='detail', width=600, height=300)
                    ])

The image will be automatically resized to all of the specified sizes. If
the target aspect ratio is different from the original aspect ratio, the size
that is wider/higher is cropped so that only the middle part of it remains.
For example, if the original image has 1600x600 pixel and the target size is
600x300 ('detail' size in the above example), it will be scaled to 50%
(800x300 pixel) and then 100 pixel to the left and 100 to the right will be
cropped to reach the target size.

If no explicit MIME type for `adhocracy_core.schema.Image` is specified, the
default is "image/", i.e., images of any type are accepted.

Uploading Files and Posting Resources that Refer to Files
---------------------------------------------------------

This section concerns the REST API.

