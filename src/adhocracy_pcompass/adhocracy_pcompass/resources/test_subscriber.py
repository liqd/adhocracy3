from pytest import fixture, mark
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
            sheets.name.IName.__identifier__: {'name': 'dataset_1'}}
        external_resource = registry.content.create(
            resources.external_resource.IExternalResource.__identifier__,
            parent=context,
            appstructs=er_appstructs)
        return context

    def make_comment(self, registry, context):
        from adhocracy_core import resources, sheets

        comment = registry.content.create(
            resources.comment.IComment.__identifier__,
            parent=context['dataset_1'])
        registry.content.create(
            resources.comment.ICommentVersion.__identifier__,
            parent=comment,
            appstructs={
                sheets.comment.IComment.__identifier__: {
                    'content': 'This is a comment',
                    'refers_to': context['dataset_1']
                }
            })

    def requests_post(self, status_code=200):
        response = requests.Response
        response.status_code = status_code
        post = Mock(name="requests.post", return_value=response)
        return(post)

    def test_elastic_search_update(self, registry, context, monkeypatch):
        from .subscriber import update_elasticsearch_policycompass

        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        self.make_comment(registry, context)

        requests_post.assert_called_with(
            'http://localhost:9000/policycompass_search/dataset/1/_update',
            json={'doc': {'comment_count': 1}})
