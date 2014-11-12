File and Image Upload
=====================

TODO All of this still needs to be implemented. This document will be
revised and made testable along with the implementation.

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
                        ImageSize(name='thumbnail, width=160, height=120)
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

