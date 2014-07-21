import unittest
from mock import patch

import colander
from pyramid import testing
import pytest

from adhocracy.utils import get_sheet


class PasswordSheetUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.sheets.user import IPasswordAuthentication
        from adhocracy.sheets.user import password_metadata
        self.metadata = password_metadata
        self.context = testing.DummyResource(__provides__=IPasswordAuthentication)

    def _makeOne(self, metadata, context):
        from adhocracy.sheets.user import PasswordAuthenticationSheet
        return PasswordAuthenticationSheet(metadata, context)

    def test_set_password(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.set({'password': 'test'})
        assert len(inst.context.password) == 60

    def test_reset_password(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.set({'password': 'test'})
        password_old = inst.context.password
        inst.set({'password': 'test'})
        password_new = inst.context.password
        assert password_new != password_old

    def test_set_empty_password(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.set({'password': ''})
        assert not hasattr(inst.context, 'password')

    def test_get_password(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.context.password = 'test'
        assert inst.get()['password'] == 'test'

    def test_get_empty_password(self):
        inst = self._makeOne(self.metadata, self.context)
        assert inst.get()['password'] == ''

    def test_check_password_valid(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.set({'password': 'test'})
        assert inst.check_plaintext_password('test')

    def test_check_password_not_valid(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.set({'password': 'test'})
        assert not inst.check_plaintext_password('wrong')

    def test_check_password_is_to_long(self):
        inst = self._makeOne(self.metadata, self.context)
        password = 'x' * 40026
        with pytest.raises(ValueError):
            inst.check_plaintext_password(password)


class UserSheetsIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.sheets.user')

    def tearDown(self):
        testing.tearDown()

    def test_add_userbasic_sheet_to_registry(self):
        from adhocracy.sheets.user import IUserBasic
        context = testing.DummyResource(__provides__=IUserBasic)
        inst = get_sheet(context, IUserBasic)
        assert inst.meta.isheet is IUserBasic

    def test_add_password_sheet_to_registry(self):
        from adhocracy.sheets.user import PasswordAuthenticationSheet
        from adhocracy.sheets.user import IPasswordAuthentication
        context = testing.DummyResource(__provides__=IPasswordAuthentication)
        inst = get_sheet(context, IPasswordAuthentication)
        assert inst.meta.isheet is IPasswordAuthentication
        assert isinstance(inst, PasswordAuthenticationSheet)


class UserBasicSchemaSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.sheets.user import UserBasicSchema
        return UserBasicSchema()

    def test_deserialize_all(self):
        inst = self.make_one()
        cstruct = {'email': 'test@test.de',
                   'name': 'login',
                   'tzname': 'Europe/Berlin'}
        assert inst.deserialize(cstruct) == cstruct

    def test_deserialize_name_missing(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_name_empty(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'name': ''})

    def test_deserialize_name(self):
        inst = self.make_one()
        assert inst.deserialize({'name': 'login'}) == {'name': 'login'}

    def test_name_has_deferred_validator(self):
        inst = self.make_one()
        assert isinstance(inst['name'].validator, colander.deferred)

    def test_email_has_deferred_validator(self):
        inst = self.make_one()
        assert isinstance(inst['email'].validator, colander.deferred)


class DeferredValidateUserName(unittest.TestCase):

    @patch('adhocracy.resources.principal.UserLocatorAdapter')
    def setUp(self, mock_user_locator=None):
        from zope.interface import Interface
        from substanced.interfaces import IUserLocator
        config = testing.setUp()
        self.request = testing.DummyRequest(root=testing.DummyResource(),
                                            registry=config.registry)
        self.user_locator = mock_user_locator
        config.registry.registerAdapter(self.user_locator,
                                        required=(Interface, Interface),
                                        provided=IUserLocator)
        self.node = colander.MappingSchema()
        self.user_locator = mock_user_locator

    def _call_fut(self, node, kw):
        from adhocracy.sheets.user import deferred_validate_user_name
        return deferred_validate_user_name(node, kw)

    def test_name_is_empty_and_no_request_kw(self):
        self.user_locator.return_value.get_user_by_login.return_value = None
        validator = self._call_fut(self.node, {})
        assert validator is None

    def test_name_is_empty(self):
        self.user_locator.return_value.get_user_by_login.return_value = None
        validator = self._call_fut(self.node, {'request': self.request})
        assert validator(self.node, '') is None

    def test_name_is_unique(self):
        self.user_locator.return_value.get_user_by_login.return_value = None
        validator = self._call_fut(self.node, {'request': self.request})
        assert validator(self.node, 'unique') is None

    def test_name_is_not_unique(self):
        self.user_locator.return_value.get_user_by_login.return_value = object()
        validator = self._call_fut(self.node, {'request': self.request})
        with pytest.raises(colander.Invalid):
            validator(self.node, 'not unique')


class DeferredValidateUserEmail(unittest.TestCase):

    @patch('adhocracy.resources.principal.UserLocatorAdapter')
    def setUp(self, mock_user_locator=None):
        from zope.interface import Interface
        from substanced.interfaces import IUserLocator
        config = testing.setUp()
        self.request = testing.DummyRequest(root=testing.DummyResource(),
                                            registry=config.registry)
        self.user_locator = mock_user_locator
        config.registry.registerAdapter(self.user_locator,
                                        required=(Interface, Interface),
                                        provided=IUserLocator)
        self.node = colander.MappingSchema()
        self.user_locator = mock_user_locator

    def _call_fut(self, node, kw):
        from adhocracy.sheets.user import deferred_validate_user_email
        return deferred_validate_user_email(node, kw)

    def test_email_is_empty(self):
        validator = self._call_fut(self.node, {'request': self.request})
        with pytest.raises(colander.Invalid):
            validator(self.node, '') is None

    def test_email_is_wrong(self):
        validator = self._call_fut(self.node, {'request': self.request})
        with pytest.raises(colander.Invalid):
             validator(self.node, 'wrong_email') is None

    def test_email_is_unique(self):
        self.user_locator.return_value.get_user_by_email.return_value = None
        validator = self._call_fut(self.node, {'request': self.request})
        assert validator(self.node, 'test@test.de') is None

    def test_email_is_not_unique(self):
        self.user_locator.return_value.get_user_by_email.return_value = object()
        validator = self._call_fut(self.node, {'request': self.request})
        with pytest.raises(colander.Invalid):
            validator(self.node, 'not unique')