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

    def delete_comment(self, comment, registry):
        from adhocracy_core import sheets
        metadata = registry.content.get_sheet(comment,
                                              sheets.metadata.IMetadata)
        metadata.set({ 'hidden': True })

    def requests_post(self, status_code=200):
        response = requests.Response
        response.status_code = status_code
        post = Mock(name='requests.post', return_value=response)
        return(post)

    def test_notify_policycompass_on_create(self, registry, context, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        self.make_comment(registry, context)

        requests_post.assert_called_with(
            'http://localhost:8000/api/v1/searchmanager/updateindexitem/' \
            'dataset/478')

    def test_notify_policycompass_on_delete(self, registry, context, monkeypatch):
        requests_post = self.requests_post()
        monkeypatch.setattr(requests, 'post', requests_post)
        comment = self.make_comment(registry, context)

        self.delete_comment(comment, registry)
        requests_post.assert_called_with(
            'http://localhost:8000/api/v1/searchmanager/updateindexitem/' \
            'dataset/478')

    def test_notify_policycompass_error(self, registry, context, monkeypatch):
        requests_post = self.requests_post(400)
        monkeypatch.setattr(requests, 'post', requests_post)
        with raises(ValueError):
            self.make_comment(registry, context)
