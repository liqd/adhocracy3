from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import mark


class TestIndexUserText:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def call_fut(self, *args):
        from .system import index_user_text
        return index_user_text(*args)

    def test_return_user_name(self, registry, context, mock_sheet):
        from copy import deepcopy
        context.__name__ = '0000006'
        user_basic_sheet = deepcopy(mock_sheet)
        user_basic_sheet.get.return_value = {'name': 'user_name'}
        user_extended_sheet = deepcopy(mock_sheet)
        user_extended_sheet.get.return_value = {'email': 'user@example.com'}
        registry.content.get_sheet.side_effect = [user_basic_sheet,
                                                  user_extended_sheet]
        result = self.call_fut(context, 'default')
        assert result == '0000006 ' \
                         'user_name user name ' \
                         'user@example.com user@example com'
