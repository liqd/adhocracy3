from pytest import fixture, mark, raises
from unittest.mock import Mock

import requests


@mark.usefixtures('integration')
class TestUpdateElasticsearchPolicycompass:

    @fixture
    def registry(self, config):
        return config.registry

    @fixture
    def context(self, registry, pool_with_catalogs):
        from adhocracy_core import resources, sheets

        context = pool_with_catalogs
        er_appstructs = {
            sheets.name.IName.__identifier__: {'name': 'dataset_478'}}
        external_resource = registry.content.create(
            resources.external_resource.IExternalResource.__identifier__,
            parent=context,
            appstructs=er_appstructs)
        return context

    def make_comment(self, registry, context):
        from adhocracy_core import resources, sheets

        comment = registry.content.create(
            resources.comment.IComment.__identifier__,
            parent=context['dataset_478'])
        registry.content.create(
            resources.comment.ICommentVersion.__identifier__,
            parent=comment,
            appstructs={
                sheets.comment.IComment.__identifier__: {
                    'content': 'This is a comment',
                    'refers_to': context['dataset_478']
                }
            })
        return comment

    def delete_comment(self, comment, registry, context):
        from adhocracy_core import utils, resources, sheets

        metadata = utils.get_sheet(comment, sheets.metadata.IMetadata, registry)
        metadata.set({ 'hidden': True })

    def requests_post(self, status_code=200):
        response = requests.Response
        response.status_code = status_code
        post = Mock(name='requests.post', return_value=response)
        return(post)

    def test_elastic_search_update_on_create(self, registry, context, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        self.make_comment(registry, context)

        requests_post.assert_called_with(
            'http://localhost:9000/policycompass_search/dataset/478/_update',
            json={'doc': {'comment_count': 1}})

    def test_elastic_search_update_on_delete(self, registry, context, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        comment = self.make_comment(registry, context)

        self.delete_comment(comment, registry, context)
        requests_post.assert_called_with(
            'http://localhost:9000/policycompass_search/dataset/478/_update',
            json={'doc': {'comment_count': 0}})

    def test_elastic_search_update_not_found(self, registry, context, monkeypatch):
        requests_post = self.requests_post(404)
        monkeypatch.setattr(requests, 'post', requests_post)
        self.make_comment(registry, context)

    def test_elastic_search_update_error(self, registry, context, monkeypatch):
        requests_post = self.requests_post(400)
        monkeypatch.setattr(requests, 'post', requests_post)
        with raises(ValueError):
            self.make_comment(registry, context)
