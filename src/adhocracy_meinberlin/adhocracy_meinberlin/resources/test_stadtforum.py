from pytest import fixture
from pytest import mark


def test_polarizedcomment_meta():
    from .stadtforum import polarizedcomment_meta
    from .stadtforum import IPolarizedComment
    from .stadtforum import IPolarizedCommentVersion
    meta = polarizedcomment_meta
    assert meta.iresource is IPolarizedComment
    assert meta.item_type == IPolarizedCommentVersion
    assert meta.element_types == (IPolarizedCommentVersion,)
    assert meta.use_autonaming
    assert meta.permission_create == 'create_comment'


def test_polarizedcommentversion_meta():
    from .stadtforum import polarizedcommentversion_meta
    from .stadtforum import IPolarizedCommentVersion
    import adhocracy_core.sheets
    meta = polarizedcommentversion_meta
    assert meta.iresource is IPolarizedCommentVersion
    assert meta.extended_sheets == (adhocracy_core.sheets.comment.IComment,
                                    adhocracy_core.sheets.comment.ICommentable,
                                    adhocracy_core.sheets.rate.IRateable,
                                    adhocracy_core.sheets.polarization.IPolarizable,
    )
    assert meta.permission_create == 'edit_comment'


@mark.usefixtures('integration')
class TestRoot:

    @fixture
    def context(self, pool):
        return pool

    def test_create_polarizedcomment(self, context, registry):
        from adhocracy_meinberlin.resources.stadtforum import IPolarizedComment
        res = registry.content.create(IPolarizedComment.__identifier__, context)
        assert IPolarizedComment.providedBy(res)

    def test_create_polarizedcommentversion(self, context, registry):
        from adhocracy_meinberlin.resources.stadtforum import IPolarizedCommentVersion
        res = registry.content.create(IPolarizedCommentVersion.__identifier__, context)
        assert IPolarizedCommentVersion.providedBy(res)

class TestProcess:

    @fixture
    def meta(self):
        from .stadtforum import process_meta
        return process_meta

    def test_meta(self, meta):
        from .stadtforum import IProcess
        assert meta.iresource is IProcess
        assert meta.workflow_name == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
