from pyramid import testing
from pytest import fixture


class TestIncludeme:

    def test_includeme_register_userinfo_sheet(self, config):
        from adhocracy_core.sheets.mercator import IUserInfo
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IUserInfo)
        assert get_sheet(context, IUserInfo)

    def test_includeme_register_organizationinfo_sheet(self, config):
        from adhocracy_core.sheets.mercator import IOrganizationInfo
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IOrganizationInfo)
        assert get_sheet(context, IOrganizationInfo)

    def test_includeme_register_introduction_sheet(self, config):
        from adhocracy_core.sheets.mercator import IIntroduction
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IIntroduction)
        assert get_sheet(context, IIntroduction)

    def test_includeme_register_details_sheet(self, config):
        from adhocracy_core.sheets.mercator import IDetails
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IDetails)
        assert get_sheet(context, IDetails)

    def test_includeme_register_motivation_sheet(self, config):
        from adhocracy_core.sheets.mercator import IMotivation
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IMotivation)
        assert get_sheet(context, IMotivation)

    def test_includeme_register_finance_sheet(self, config):
        from adhocracy_core.sheets.mercator import IFinance
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IFinance)
        assert get_sheet(context, IFinance)

    def test_includeme_register_extras_sheet(self, config):
        from adhocracy_core.sheets.mercator import IExtras
        from adhocracy_core.utils import get_sheet
        config.include('adhocracy_core.sheets.mercator')
        context = testing.DummyResource(__provides__=IExtras)
        assert get_sheet(context, IExtras)


class TestUserInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import userinfo_meta
        return userinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IUserInfo
        from adhocracy_core.sheets.mercator import UserInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IUserInfo
        assert inst.meta.schema_class == UserInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'email': '',
                  'family_name': '',
                  'personal_name': ''}
        assert inst.get() == wanted


class TestOrganizationInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import organizationinfo_meta
        return organizationinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IOrganizationInfo
        from adhocracy_core.sheets.mercator import OrganizationInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IOrganizationInfo
        assert inst.meta.schema_class == OrganizationInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'city': '',
                  'cooperation_explanation': '',
                  'country': 'DE',
                  'description': '',
                  'email': '',
                  'name': '',
                  'postcode': '',
                  'size': '0+',
                  'status': 'other',
                  'status_other': '',
                  'street_address': ''}
        assert inst.get() == wanted


class TestIntroductionSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import introduction_meta
        return introduction_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IIntroduction
        from adhocracy_core.sheets.mercator import IntroductionSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IIntroduction
        assert inst.meta.schema_class == IntroductionSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'teaser': '', 'title': ''}
        assert inst.get() == wanted


class TestDetailsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import details_meta
        return details_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IDetails
        from adhocracy_core.sheets.mercator import DetailsSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IDetails
        assert inst.meta.schema_class == DetailsSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'description': '',
                  'location_is_city': False,
                  'location_is_country': False,
                  'location_is_linked_to_ruhr': False,
                  'location_is_online': False,
                  'location_is_town': False,
                  'story': ''}
        assert inst.get() == wanted


class TestMotivationSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import motivation_meta
        return motivation_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IMotivation
        from adhocracy_core.sheets.mercator import MotivationSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IMotivation
        assert inst.meta.schema_class == MotivationSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'outcome': '', 'partners': '', 'steps': '', 'value': ''}
        assert inst.get() == wanted


class TestFinanceSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import finance_meta
        return finance_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IFinance
        from adhocracy_core.sheets.mercator import FinanceSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IFinance
        assert inst.meta.schema_class == FinanceSchema

    def test_get_empty(self, meta, context):
        from decimal import Decimal
        inst = meta.sheet_class(meta, context)
        wanted = {'budget': Decimal(0),
                  'granted': False,
                  'requested_funding': Decimal(0)}
        assert inst.get() == wanted


class TestExtrasSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.mercator import extras_meta
        return extras_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.mercator import IExtras
        from adhocracy_core.sheets.mercator import ExtrasSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IExtras
        assert inst.meta.schema_class == ExtrasSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'experience': '',
                  'heard_elsewhere': '',
                  'heard_from_colleague': False,
                  'heard_from_facebook': False,
                  'heard_from_newsletter': False,
                  'heard_from_website': False}
        assert inst.get() == wanted

