import unittest

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

    def test_get_password(self):
        inst = self._makeOne(self.metadata, self.context)
        inst.context.password = 'test'
        assert inst.get()['password'] == 'test'

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

