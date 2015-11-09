from pytest import fixture
from pytest import mark


class TestPitch:

    @fixture
    def meta(self):
        from .mercator2 import pitch_meta
        return pitch_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        assert meta.iresource == mercator2.IPitch
        assert meta.permission_create == 'create_proposal'
        assert meta.autonaming_prefix == 'pitch'
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.IPitch,
             adhocracy_core.sheets.description.IDescription,
             adhocracy_core.sheets.comment.ICommentable,)

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestPartners:

    @fixture
    def meta(self):
        from .mercator2 import partners_meta
        return partners_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        assert meta.iresource == mercator2.IPartners
        assert meta.permission_create == 'create_proposal'
        assert meta.autonaming_prefix == 'partners'
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.IPartners,
             adhocracy_core.sheets.comment.ICommentable,)

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestDuration:

    @fixture
    def meta(self):
        from .mercator2 import duration_meta
        return duration_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        assert meta.iresource == mercator2.IDuration
        assert meta.permission_create == 'create_proposal'
        assert meta.autonaming_prefix == 'duration'
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.IDuration,
             adhocracy_core.sheets.comment.ICommentable,)

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestRoadToImpact:

    @fixture
    def meta(self):
        from .mercator2 import road_to_impact_meta
        return road_to_impact_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        assert meta.iresource == mercator2.IRoadToImpact
        assert meta.permission_create == 'create_proposal'
        assert meta.autonaming_prefix == 'road_to_impact'
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.IRoadToImpact,
             adhocracy_core.sheets.comment.ICommentable,)

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestSelectionCriteria:

    @fixture
    def meta(self):
        from .mercator2 import selection_criteria_meta
        return selection_criteria_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        assert meta.iresource == mercator2.ISelectionCriteria
        assert meta.permission_create == 'create_proposal'
        assert meta.autonaming_prefix == 'selection_criteria'
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.ISelectionCriteria,
             adhocracy_core.sheets.comment.ICommentable,)

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestMercatorProposal:

    @fixture
    def meta(self):
        from .mercator2 import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        import adhocracy_core.sheets
        from adhocracy_mercator.resources import mercator2
        from adhocracy_core.resources.comment import add_commentsservice
        from adhocracy_core.resources.rate import add_ratesservice
        from adhocracy_core.resources.logbook import add_logbook_service
        from adhocracy_core.sheets.badge import IBadgeable
        assert meta.iresource == mercator2.IMercatorProposal
        assert meta.element_types == (mercator2.IPitch,
                                      mercator2.IPartners,
                                      mercator2.IRoadToImpact,
                                      mercator2.ISelectionCriteria,
                                      )
        assert meta.extended_sheets == \
            (adhocracy_core.sheets.badge.IBadgeable,
             adhocracy_core.sheets.title.ITitle,
             adhocracy_core.sheets.description.IDescription,
             adhocracy_core.sheets.comment.ICommentable,
             adhocracy_core.sheets.rate.IRateable,
             adhocracy_core.sheets.image.IImageReference,
             adhocracy_mercator.sheets.mercator2.IMercatorSubResources,
             adhocracy_mercator.sheets.mercator2.IUserInfo,
             adhocracy_mercator.sheets.mercator2.IOrganizationInfo,
             adhocracy_mercator.sheets.mercator2.ITopic,
             adhocracy_mercator.sheets.mercator2.ILocation,
             adhocracy_mercator.sheets.mercator2.IStatus,
             adhocracy_mercator.sheets.mercator2.IFinancialPlanning,
             adhocracy_mercator.sheets.mercator2.IExtraFunding,
             adhocracy_mercator.sheets.mercator2.ICommunity,
             adhocracy_mercator.sheets.mercator2.IWinnerInfo)
        assert meta.is_implicit_addable
        assert add_ratesservice in meta.after_creation
        assert add_commentsservice in meta.after_creation
        assert add_logbook_service in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)


class TestProcess:

    @fixture
    def meta(self):
        from .mercator2 import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources.process
        from adhocracy_core.resources.asset import add_assets_service
        from .mercator2 import IProcess
        from .mercator2 import IMercatorProposal
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(adhocracy_core.resources.process.IProcess)
        assert meta.element_types == (IMercatorProposal,)
        assert meta.workflow_name == 'mercator2'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
