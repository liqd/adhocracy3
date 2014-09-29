from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.registry')
    config.include('pyramid_mailer.testing')


class TestSendMail():

    @mark.usefixtures('integration')
    def test_send_mail_successfully(self, registry):
        from adhocracy_core.messaging import send_mail, _get_mailer
        mailer = _get_mailer(registry)
        assert len(mailer.outbox) == 0
        send_mail(registry=registry,
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

    @mark.usefixtures('integration')
    def test_send_mail_successfully_no_html(self, registry):
        from adhocracy_core.messaging import send_mail, _get_mailer
        mailer = _get_mailer(registry)
        assert len(mailer.outbox) == 0
        send_mail(registry=registry,
              subject='Test mail',
              recipients=['user@example.org'],
              sender='admin@example.com',
              body='Blah!')
        assert len(mailer.outbox) == 1
        msg = str(mailer.outbox[0].to_message())
        assert 'Content-Type: text/html' not in msg

    @mark.usefixtures('integration')
    def test_send_mail_successfully_neither_body_nor_html(self, registry):
        from adhocracy_core.messaging import send_mail, _get_mailer
        mailer = _get_mailer(registry)
        assert len(mailer.outbox) == 0
        with raises(ValueError):
            send_mail(registry=registry,
                  subject='Test mail',
                  recipients=['user@example.org'],
                  sender='admin@example.com')

    @mark.usefixtures('integration')
    def test_send_mail_no_recipient(self, registry):
        from adhocracy_core.messaging import send_mail, _get_mailer
        mailer = _get_mailer(registry)
        assert len(mailer.outbox) == 0
        with raises(ValueError):
            send_mail(registry=registry,
                  subject='Test mail',
                  recipients=None,
                  sender='admin@example.com',
                  body='Blah!',
                  html='<p>Bäh!</p>')
