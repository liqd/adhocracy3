from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('pyramid_mailer.testing')
    config.include('adhocracy_core.registry')
    config.include('adhocracy_core.messaging')


@mark.usefixtures('integration')
class TestSendMail():

    def test_send_mail_successfully(self, registry):
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        registry.messenger.send_mail(
              subject='Test mail',
              recipients=['user@example.org'],
              sender='admin@example.com',
              body='Blah!',
              html='<p>Bäh!</p>')
        assert len(mailer.outbox) == 1
        msg = str(mailer.outbox[0].to_message())
        assert 'Test mail' in msg
        assert 'Blah' in msg
        assert 'Content-Type: text/html' in msg

    def test_send_mail_successfully_no_html(self, registry):
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        registry.messenger.send_mail(
              subject='Test mail',
              recipients=['user@example.org'],
              sender='admin@example.com',
              body='Blah!')
        assert len(mailer.outbox) == 1
        msg = str(mailer.outbox[0].to_message())
        assert 'Content-Type: text/html' not in msg

    def test_send_mail_successfully_neither_body_nor_html(self, registry):
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        with raises(ValueError):
            registry.messenger.send_mail(
                  subject='Test mail',
                  recipients=['user@example.org'],
                  sender='admin@example.com')

    def test_send_mail_no_recipient(self, registry):
        mailer = registry.messenger._get_mailer()
        assert len(mailer.outbox) == 0
        with raises(ValueError):
            registry.messenger.send_mail(
                  subject='Test mail',
                  recipients=None,
                  sender='admin@example.com',
                  body='Blah!',
                  html='<p>Bäh!</p>')


@mark.usefixtures('integration')
class TestRenderAndSendMail:

    @fixture
    def mock_resource_exists(self, registry):
        from adhocracy_core.messaging import Messenger
        mock_resource_exists = Mock(spec=Messenger._resource_exists)
        registry.messenger._resource_exists = mock_resource_exists
        return mock_resource_exists

    @fixture
    def mock_render(self, registry):
        from adhocracy_core.messaging import Messenger
        mock_render = Mock(spec=Messenger._render)
        registry.messenger._render = mock_render
        return mock_render

    def test_render_and_send_mail_both_templates_exist(self, registry,
                                                       mock_resource_exists,
                                                       mock_render):
        mock_resource_exists.return_value = True
        registry.messenger.render_and_send_mail(
            subject='Test mail',
            recipients=['user@example.org'],
            template_asset_base='adhocracy_core:foo',
            args={'name': 'value'})
        assert mock_resource_exists.call_count == 2
        assert mock_resource_exists.call_args == (
            ('adhocracy_core', 'foo.html.mako'),)
        assert mock_render.call_count == 2
        assert mock_render.call_args == (
            ('adhocracy_core:foo.html.mako', {'name': 'value'}),)

    def test_render_and_send_mail_no_template_exist(self, registry,
                                                    mock_resource_exists,
                                                    mock_render):
        mock_resource_exists.return_value = False
        with raises(ValueError):
            registry.messenger.render_and_send_mail(
                subject='Test mail',
                recipients=['user@example.org'],
                template_asset_base='adhocracy_core:foo',
                args={'name': 'value'})
        assert mock_resource_exists.call_count == 2
        assert not mock_render.called
