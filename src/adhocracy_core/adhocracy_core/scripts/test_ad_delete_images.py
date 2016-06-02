from pyramid import testing
from unittest.mock import Mock
from pytest import fixture


class TestDeleteNotReferencedImages:

    def call_fut(self, *args):
        from .ad_delete_images import delete_not_referenced_images
        return delete_not_referenced_images(*args)

    @fixture
    def context(self, context):
        context.__del__ = Mock()
        return context

    @fixture
    def mock_catalogs(self, monkeypatch, mock_catalogs):
        from . import ad_delete_images
        monkeypatch.setattr(ad_delete_images, 'find_service',
                            lambda x, y: mock_catalogs)
        return mock_catalogs

    @fixture
    def mock_now(self, monkeypatch):
        from . import ad_delete_images
        from datetime import datetime
        mock = Mock(return_value=datetime(2016, 1, 11))
        monkeypatch.setattr(ad_delete_images, 'now', mock)
        return mock

    def test_ignore_no_images(self, context, mock_catalogs):
        assert self.call_fut(context, 10) is None

    def test_ignore_images_younger_then_max_age(self, context, mock_catalogs,
                                                search_result, query, mock_now):
        import datetime
        from adhocracy_core.resources.image import IImage
        image = testing.DummyResource()
        context['image'] = image
        mock_now.return_value = datetime.datetime(2016, 1, 11)
        mock_catalogs.search.return_value = search_result
        self.call_fut(context, 10)
        assert mock_catalogs.search.call_args_list[0][0][0] == \
            query._replace(interfaces=IImage,
                           indexes={'item_creation_date':
                                    ('lt', datetime.datetime(2016, 1, 1))
                                   },
                           resolve=True)
        assert 'image' in context

    def test_ignore_images_that_are_referenced(self, context, mock_catalogs,
                                               search_result, query):
        from adhocracy_core.interfaces import Reference
        from adhocracy_core.sheets.image import IImageReference
        image = testing.DummyResource()
        context['image'] = image
        mock_catalogs.search.side_effect = [
            search_result._replace(elements=[image]),
            search_result]
        self.call_fut(context, 10)
        assert mock_catalogs.search.call_args_list[1][0][0] == \
            query._replace(references=((Reference(None, IImageReference, '',
                                                  image)),),
                           )
        assert 'image' in context

    def test_delete_images_not_referenced_and_older_then_max_age(
            self, context, mock_catalogs, search_result):
        image = testing.DummyResource()
        context['image'] = image
        referencing = testing.DummyResource(__parent__=context)
        mock_catalogs.search.side_effect = [
            search_result._replace(elements=[image]),
            search_result._replace(elements=[referencing],
                                   count=1)]
        self.call_fut(context, 10)
        assert 'image' not in context


