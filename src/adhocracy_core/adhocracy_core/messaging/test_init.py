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
    config.include('adhocracy_core.sheets.principal')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.messaging')


@mark.usefixtures('integration')
class TestSendMail:

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


class TestSendMailToQueue:

    def test_send_mail_to_queue(self, config, registry, request_):
        config.include('pyramid_mailer.testing')
        config.include('adhocracy_core.content')
        registry['config'].adhocracy.use_mail_queue = True
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


def _msg_to_str(msg):
    """Convert an email message into a string."""
    # The DummyMailer is too stupid to use a default sender, hence we add
    # one manually, if necessary
    if msg.sender is None:
        msg.sender = 'support@unconfigured.domain'
    msgtext = str(msg.to_message())
    # Undo quoted-printable encoding of spaces for convenient testing
    return msgtext.replace('=20', ' ')


@mark.usefixtures('integration')
class TestSendAbuseComplaint:

    def test_send_abuse_complaint_with_user(self, request_, registry):
        from adhocracy_core.sheets.principal import IUserBasic
        user = testing.DummyResource(__provides__=IUserBasic,
                                     name='Alex User')
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

    def test_send_abuse_complaint_without_user(self, request_, registry):
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
class TestSendMessageToUser:

    def test_send_message_to_user(self, request_, registry):
        from adhocracy_core.sheets.principal import IUserExtended
        from adhocracy_core.sheets.principal import IUserBasic
        settings = registry['config'].configurator
        settings.mail.noreply_sender = 'noreply@example.org'
        recipient = testing.DummyResource(__provides__=(IUserExtended,
                                                        IUserBasic),
                                          email='recipient@example.org')
        sender = testing.DummyResource(__provides__=(IUserExtended, IUserBasic),
                                       email='sender@example.org',
                                       name='Sandy Sender')
        mailer = registry.messenger.mailer
        messenger = registry.messenger
        messenger.send_message_to_user(
            recipient=recipient,
            title='Important Adhocracy notice',
            text='Surprisingly enough, all is well.',
            request=request_,
            from_user=sender)
        msgtext = _msg_to_str(mailer.outbox[0])
        assert 'From: noreply@example.org' in msgtext
        assert 'Subject: Adhocracy Message from Sandy Sender: Important Adhocracy notice' in msgtext
        assert 'To: recipient@example.org' in msgtext


class TestSendRegistrationMail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        settings = config.registry['config']
        settings.adhocracy.use_mail_queue = False
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


class TestSendPasswordResetMail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        config.registry['config'].adhocracy.site_name = 'sitename'
        config.registry['config'].adhocracy.canonical_url = 'http://front.end'
        return config.registry

    @fixture
    def inst(self, registry):
        from . import Messenger
        return Messenger(registry)

    def test_send_password_reset_mail(self, inst, request_):
        inst.send_mail = Mock()
        user = testing.DummyResource(name='Anna', email='anna@example.org')
        reset = testing.DummyResource(__name__='/reset')
        inst.send_password_reset_mail(user, reset, request=request_)
        assert inst.send_mail.call_args[1]['recipients'] == ['anna@example.org']
        assert inst.send_mail.call_args[1]['subject'] ==\
               'mail_reset_password_subject'
        assert inst.send_mail.call_args[1]['body'] == \
               'mail_reset_password_body_txt'
        assert inst.send_mail.call_args[1]['body'].mapping ==\
            {'user_name': 'Anna',
             'site_name': 'sitename',
             'reset_url': 'http://front.end/password_reset/?path=%252Freset'}
        assert inst.send_mail.call_args[1]['request'] == request_


class TestSendInvitationMail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mako')
        config.include('pyramid_mailer.testing')
        config.registry['config'].adhocracy.site_name = 'sitename'
        config.registry['config'].adhocracy.canonical_url = 'http://front.end'
        return config.registry

    @fixture
    def inst(self, registry):
        from . import Messenger
        return Messenger(registry)

    def test_send_mail_with_password_reset_link(self, inst, request_):
        inst.send_mail = Mock()
        user = testing.DummyResource(name='Anna', email='anna@example.org')
        reset = testing.DummyResource(__name__='/reset')
        inst.send_invitation_mail(user, reset, request=request_)
        assert inst.send_mail.call_args[1]['recipients'] == ['anna@example.org']
        assert inst.send_mail.call_args[1]['subject'] ==\
               'mail_invitation_subject'
        assert inst.send_mail.call_args[1]['body'] == \
               'mail_invitation_body_txt'
        assert inst.send_mail.call_args[1]['body'].mapping ==\
            {'user_name': 'Anna',
             'site_name': 'sitename',
             'email': 'anna@example.org',
             'reset_url': 'http://front.end/password_reset/?path=%252Freset'}
        assert inst.send_mail.call_args[1]['request'] == request_

    def test_render_custom_subject(self, inst, request_):
        inst.send_mail = Mock()
        user = testing.DummyResource(name='Anna', email='anna@example.org')
        reset = testing.DummyResource(__name__='/reset')
        inst.send_invitation_mail(user, reset, request=request_,
                                  subject_tmpl='adhocracy_core:templates/invite_subject_sample.txt.mako')
        assert inst.send_mail.call_args[1]['subject'] == 'Welcome Anna to sitename.'

    def test_render_custom_body(self, inst, request_):
        inst.send_mail = Mock()
        user = testing.DummyResource(name='Anna', email='anna@example.org')
        reset = testing.DummyResource(__name__='/reset')
        inst.send_invitation_mail(user, reset, request=request_,
                                  body_tmpl='adhocracy_core:templates/invite_body_sample.txt.mako')
        assert inst.send_mail.call_args[1]['body'] ==\
               'Hi Anna,\n'\
               'please reset your password here http://front.end/password_reset/?path=%252Freset to join sitename.'


class TestActivityEmail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        config.registry['config'].adhocracy.site_name = 'sitename'
        config.registry['config'].adhocracy.canonical_url = 'http://front.end'
        return config.registry

    @fixture
    def inst(self, registry):
        from . import Messenger
        return Messenger(registry)

    @fixture
    def user(self):
        return testing.DummyResource()

    @fixture
    def activity(self, activity):
        context = testing.DummyResource(__name__='object')
        target = testing.DummyResource(__name__='target')
        return activity._replace(object=context, target=target)

    def test_send_activity(self, inst, user, activity, request_, mocker):
        inst.send_mail = Mock()
        inst._get_user_email = Mock(return_value='anna@example.org')
        translate_description = mocker.patch(
            'adhocracy_core.messaging.generate_activity_description',
            autospec=True)

        inst.send_activity_mail(user, activity, request_)

        inst._get_user_email.assert_called_with(user)
        send_mail_args = inst.send_mail.call_args[1]
        wanted_mapping = {'site_name': 'sitename',
                          'object_url': 'http://front.end/robject/',
                          'target_url': 'http://front.end/rtarget/',
                          'activity_name': activity.name,
                          'activity_description':
                              translate_description.return_value.default,
                          }
        assert send_mail_args['recipients'] == ['anna@example.org']
        assert send_mail_args['subject'] == 'mail_send_activity_subject'
        send_mail_args['subject'].mapping.update.assert_called_with(wanted_mapping)
        send_mail_args['body'].mapping.update.assert_called_with(wanted_mapping)
        assert send_mail_args['body'] == 'mail_send_activity_add_update_body_txt'
        assert send_mail_args['request'] == request_

    def test_send_activity_remove(self, inst, user, activity, request_, mocker):
        from adhocracy_core.interfaces import ActivityType
        inst.send_mail = Mock()
        inst._get_user_email = Mock(return_value='anna@example.org')
        translate_description = mocker.patch(
            'adhocracy_core.messaging.generate_activity_description')
        activity = activity._replace(type=ActivityType.remove)
        inst.send_activity_mail(user, activity, request_)
        send_mail_args = inst.send_mail.call_args[1]
        assert send_mail_args['body'] == 'mail_send_activity_remove_body_txt'


class TestSendPasswordChangeMail:

    @fixture
    def registry(self, config):
        config.include('pyramid_mailer.testing')
        config.registry['config'].adhocracy.site_name = 'sitename'
        config.registry['config'].adhocracy.canonical_url = 'http://front.end'
        return config.registry

    @fixture
    def inst(self, registry):
        from . import Messenger
        return Messenger(registry)

    def test_send_password_change_mail(self, inst, request_):
        inst.send_mail = Mock()
        user = testing.DummyResource(name='Anna', email='anna@example.org')
        inst.send_password_change_mail(user, request=request_)
        assert inst.send_mail.call_args[1]['recipients'] == ['anna@example.org']
        assert inst.send_mail.call_args[1]['subject'] == \
               'mail_password_change_subject'
        assert inst.send_mail.call_args[1]['body'] == \
               'mail_password_change_body_txt'
        assert inst.send_mail.call_args[1]['body'].mapping == \
               {'user_name': 'Anna',
                'site_name': 'sitename',
                'create_reset_url': 'http://front.end/create_password_reset/'}
        assert inst.send_mail.call_args[1]['request'] == request_
