from pytest import fixture, mark
from unittest.mock import Mock

import requests


@mark.usefixtures('integration')
class TestUpdateElasticsearchPolicycompass:

    @fixture
    def registry(self, config):
        return config.registry


    def make_external_resource(self, name, registry, pool_with_catalogs):
        from adhocracy_core import resources, sheets

        context = pool_with_catalogs
        er_appstructs = {
            sheets.name.IName.__identifier__: {'name': name}}
        external_resource = registry.content.create(
            resources.external_resource.IExternalResource.__identifier__,
            parent=context,
            appstructs=er_appstructs)
        return context

    @fixture
    def context_r1(self, registry, pool_with_catalogs):
        return self.make_external_resource('dataset_1',
                                           registry,
                                           pool_with_catalogs)

    @fixture
    def context_r2(self, registry, pool_with_catalogs):
        return self.make_external_resource('dataset_2',
                                           registry,
                                           pool_with_catalogs)

    def make_comment(self, resource_name, registry, context):
        from adhocracy_core import resources, sheets

        comment = registry.content.create(
            resources.comment.IComment.__identifier__,
            parent=context[resource_name])
        registry.content.create(
            resources.comment.ICommentVersion.__identifier__,
            parent=comment,
            appstructs={
                sheets.comment.IComment.__identifier__: {
                    'content': 'This is a comment',
                    'refers_to': context[resource_name]
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

    def test_elastic_search_update_on_create(self, registry, context_r1, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        self.make_comment('dataset_1', registry, context_r1)

        requests_post.assert_called_with(
            'http://localhost:9000/policycompass_search/dataset/1/_update',
            json={'doc': {'comment_count': 1}})

    def test_elastic_search_update_on_delete(self, registry, context_r2, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        comment = self.make_comment('dataset_2', registry, context_r2)

        self.delete_comment(comment, registry, context_r2)
        requests_post.assert_called_with(
            'http://localhost:9000/policycompass_search/dataset/2/_update',
            json={'doc': {'comment_count': 0}})
