import unittest

from pyramid import testing
import pytest


class TokenManagerUnitTest(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        self.context = testing.DummyResource()
        self.secret = 'secret'
        self.user_id = '/principals/user/1'
        self.token = 'secret'
        self.timestamp = datetime.now()

    def _make_one(self, context, secret='', timeout=None):
        from adhocracy.authentication import TokenMangerAnnotationStorage
        return TokenMangerAnnotationStorage(context, secret, timeout=timeout)

    def test_create(self):
        from adhocracy.interfaces import ITokenManger
        from zope.interface.verify import verifyObject
        inst = self._make_one(self.context, self.secret)
        assert verifyObject(ITokenManger, inst)
        assert ITokenManger.providedBy(inst)

    def test_create_token_with_user_id_first_time(self):
        inst = self._make_one(self.context, self.secret)
        token = inst.create_token(self.user_id)
        assert len(token) >= 128

    def test_create_token_with_user_id_second_time(self):
        inst = self._make_one(self.context, self.secret)
        token = inst.create_token(self.user_id)
        token_second = inst.create_token(self.user_id)
        assert token != token_second

    def test_get_user_id_with_existing_token(self):
        inst = self._make_one(self.context, self.secret)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        assert inst.get_user_id(self.token) == self.user_id

    def test_get_user_id_with_multiple_existing_token(self):
        inst = self._make_one(self.context, self.secret)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        token_second = 'secret_second'
        inst._token_to_user_id_date[token_second] = (self.user_id, self.timestamp)
        assert inst.get_user_id(token_second) == self.user_id

    def test_get_user_id_with_non_existing_token(self):
        inst = self._make_one(self.context, self.secret)
        with pytest.raises(KeyError):
            inst.get_user_id('wrong_token')

    def test_get_user_id_with_existing_token_but_passed_timeout(self):
        inst = self._make_one(self.context, self.secret, timeout=0)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        with pytest.raises(KeyError):
            inst.get_user_id(self.token)

    def test_delete_token_with_non_existing_user_id(self):
        inst = self._make_one(self.context, self.secret)
        assert inst.delete_token('wrong_token') == None

    def test_delete_token_with_existing_user_id(self):
        inst = self._make_one(self.context, self.secret)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        inst.delete_token(self.token)
        assert self.token not in inst._token_to_user_id_date


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import ILocation
        self.config = testing.setUp()
        self.config.include('adhocracy.authentication')
        self.context = testing.DummyResource(__provides__=ILocation)

    def test_get_adapter(self):
        from zope.component import getAdapter
        from adhocracy.interfaces import ITokenManger
        from zope.interface.verify import verifyObject
        inst = getAdapter(self.context, ITokenManger)
        assert verifyObject(ITokenManger, inst)
