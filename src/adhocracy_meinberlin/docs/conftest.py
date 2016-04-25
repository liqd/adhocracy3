"""Workaround to force fixture override for doctest."""
from pytest import fixture


@fixture(scope='class', autouse=True)  # autouse needed to make the doctest run
def app_router(app_settings):
    """Return the test wsgi application using a DB with file storage."""
    from shutil import rmtree
    from ZODB import FileStorage
    from adhocracy_core.testing import make_configurator
    import adhocracy_meinberlin
    db_file = 'var/db/test/Data.fs'
    blob_dir = 'var/db/test/blobs'
    # Delete old content
    storage = FileStorage.FileStorage(db_file, blob_dir=blob_dir)
    storage.cleanup()
    # This doesn't seem to clear the blob_dir, hence we do so manually
    rmtree(blob_dir, ignore_errors=True)
    app_settings['zodbconn.uri'] = 'file://{}?blobstorage_dir={}'.format(
        db_file, blob_dir)
    configurator = make_configurator(app_settings, adhocracy_meinberlin)
    return configurator.make_wsgi_app()
