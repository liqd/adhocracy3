from unittest.mock import Mock

from pytest import fixture
from pytest import mark
from pytest import raises
from pyramid import testing


@fixture
def integration(config):
    config.include('pyramid_mailer.testing')
    config.include('pyramid_mako')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.messaging')


@fixture
def request_(registry):
    request = testing.DummyRequest()
    request.registry = registry
    return request


@mark.usefixtures('integration')
class TestSendMail():

    def test_send_mail_with_body_and_html(self, registry, request_):
        mailer = registry.messenger.mailer
        registry.messenger.send_mail(subject='Test mail',
                                     recipients=['user@example.org'],
                                     sender='admin@example.com',
                                     body='Blah!',
                                     request=request_,
                                     html='<p>Bäh!</p>')
        msg = str(mailer.outbox[0].to_message())
        assert 'Test mail' in msg
        assert 'Blah' in msg
        assert 'Content-Type: text/html' in msg

    def test_send_mail_with_body(self, registry, request_):
        mailer = registry.messenger.mailer
        registry.messenger.send_mail(subject='Test mail',
                                     recipients=['user@example.org'],
                                     sender='admin@example.com',
                                     request=request_,
                                     body='Blah!')
        msg = str(mailer.outbox[0].to_message())
        assert 'Content-Type: text/html' not in msg

    def test_send_mail_without_body_and_html(self, registry, request_):
        with raises(ValueError):
            registry.messenger.send_mail(subject='Test mail',
                                         recipients=['user@example.org'],
                                         request=request_,
                                         sender='admin@example.com')

    def test_send_mail_no_recipient(self, registry, request_):
        with raises(ValueError):
            registry.messenger.send_mail(subject='Test mail',
                                         recipients=None,
                                         sender='admin@example.com',
                                         body='Blah!',
                                         request=request_,
                                         html='<p>Bäh!</p>')


class TestSendMailToQueue():

    def test_send_mail_to_queue(self, config, registry, request_):
        config.include('pyramid_mailer.testing')
        config.include('adhocracy_core.content')
        registry.settings['adhocracy.use_mail_queue'] = 'true'
        config.include('adhocracy_core.messaging')
        mailer = registry.messenger.mailer
        registry.messenger.send_mail(subject='Test mail',
                                     recipients=['user@example.org'],
                                     sender='admin@example.com',
                                     body='Blah!',
                                     request=request_,
                                     html='<p>Bäh!</p>')
        assert len(mailer.queue) == 1
        assert len(mailer.outbox) == 0


@mark.usefixtures('integration')
class TestRenderAndSendMail:

    @fixture
    def mock_localizer(self, request_):
        localizer = Mock()
        localizer.translate = lambda x: x
        request_.localizer = localizer
        return localizer

    @fixture
    def mock_resource_exists(self, monkeypatch):
        exists = Mock()
        monkeypatch.setattr('adhocracy_core.messaging.resource_exists', exists)
        return exists

    @fixture
    def mock_render(self, monkeypatch):
        render = Mock()
        monkeypatch.setattr('adhocracy_core.messaging.render', render)
        return render

    def test_render_and_send_mail_both_templates_exist(self, registry, request_,
                                                       mock_resource_exists,
                                                       mock_render,
                                                       mock_localizer):
        mock_resource_exists.return_value = True
        registry.messenger.render_and_send_mail(
            subject='Test mail',
            recipients=['user@example.org'],
            template_asset_base='adhocracy_core:foo',
            request=request_,
            args={'name': 'value'})
        assert mock_resource_exists.call_count == 2
        assert mock_resource_exists.call_args == (
            ('adhocracy_core', 'foo.html.mako'),)
        assert mock_render.call_count == 2
        assert mock_render.call_args == (
            ('adhocracy_core:foo.html.mako', {'name': 'value'}),)

    def test_render_and_send_mail_no_template_exist(self, registry, request_,
                                                    mock_resource_exists,
                                                    mock_render):
        mock_resource_exists.return_value = False
        with raises(ValueError):
            registry.messenger.render_and_send_mail(
                subject='Test mail',
                recipients=['user@example.org'],
                template_asset_base='adhocracy_core:foo',
                request=request_,
                args={'name': 'value'})
        assert mock_resource_exists.call_count == 2
        assert not mock_render.called


def _msg_to_str(msg):
    """Convert an email message into a string."""
    # The DummyMailer is too stupid to use a default sender, hence we add
    # one manually, if necessary
    if msg.sender is None:
        msg.sender = 'support@unconfigured.domain'
    msgtext = str(msg.to_message())
    # Undo quoted-printable encoding of spaces for convenient testing
    return msgtext.replace('=20', ' ')

def mock_get_sheet_field(context, sheet, field_name, registry):
    result = getattr(context, field_name)
    return result


@mark.usefixtures('integration')
class TestSendAbuseComplaint():

    def test_send_abuse_complaint_with_user(self, monkeypatch, registry,
                                            request_):
        from adhocracy_core import messaging
        from adhocracy_core.resources.principal import IUser
        monkeypatch.setattr(messaging, 'get_sheet_field', mock_get_sheet_field)
        user = Mock(spec=IUser)
        user.name = 'Alex User'
        mailer = registry.messenger.mailer
        messenger = registry.messenger
        messenger.abuse_handler_mail = 'abuse_handler@unconfigured.domain'
        url = 'http://localhost/blablah'
        remark = 'Too much blah!'
        messenger.send_abuse_complaint(url=url, remark=remark, user=user,
                                       request=request_)
        msgtext = _msg_to_str(mailer.outbox[0])
        assert messenger.abuse_handler_mail in msgtext
        assert url in msgtext
        assert remark in msgtext
        assert 'sent by user Alex User' in msgtext

    def test_send_abuse_complaint_without_user(self, registry, request_):
        mailer = registry.messenger.mailer
        messenger = registry.messenger
        messenger.abuse_handler_mail = 'abuse_handler@unconfigured.domain'
        url = 'http://localhost/blablah'
        remark = 'Too much blah!'
        messenger.send_abuse_complaint(url=url, remark=remark, user=None,
                                       request=request_)
        msgtext = _msg_to_str(mailer.outbox[0])
        assert 'sent by an anonymous user' in msgtext


@mark.usefixtures('integration')
class TestSendMessageToUser():

    def test_send_message_to_user(self, monkeypatch, registry, request_):
        from adhocracy_core import messaging
        from adhocracy_core.resources.principal import IUser
        recipient = Mock(spec=IUser)
        recipient.email = 'recipient@example.org'
        sender = Mock(spec=IUser)
        sender.name = 'username'
        sender.email = 'sender@example.org'
        sender.name = 'Sandy Sender'
        monkeypatch.setattr(messaging, 'get_sheet_field', mock_get_sheet_field)
        mailer = registry.messenger.mailer
        messenger = registry.messenger
        messenger.send_message_to_user(
            recipient=recipient,
            title='Important Adhocracy notice',
            text='Surprisingly enough, all is well.',
            request=request_,
            from_user=sender)
        msgtext = _msg_to_str(mailer.outbox[0])
        assert 'From: sender@example.org' in msgtext
        assert 'Subject: [Adhocracy] Message from Sandy Sender: Important Adhocracy notice' in msgtext
        assert 'To: recipient@example.org' in msgtext


class TestSendRegistrationMail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        return config.registry

    @fixture
    def inst(self, registry):
        from . import Messenger
        return Messenger(registry)

    @fixture
    def user(self):
        user = testing.DummyResource(name = 'Anna Müller',
                                     email = 'anna@example.org')
        return user

    def test_send_registration_mail(self, inst, registry, user, request_):
        mailer = inst.mailer
        inst.send_registration_mail(user, '/activate/91X', request=request_)
        msg = mailer.outbox[0]
        # The DummyMailer is too stupid to use a default sender, hence we add
        # one manually
        msg.sender = 'support@unconfigured.domain'
        text = str(msg.to_message())
        assert '/activate/91X' in text
