from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy.registry')
    config.include('pyramid_mailer.testing')


class TestSendMail():

    @mark.usefixtures('integration')
    def test_send_mail_successfully(self, registry):
        from adhocracy.messaging import send_mail, _get_mailer
        mailer = _get_mailer(registry)
        assert len(mailer.outbox) == 0
        send_mail(registry=registry,
              subject='Test mail',
              recipients=['user@example.org'],
              sender='admin@example.com',
              body='Blah!',
              html='<p>Bäh!</p>')
        assert len(mailer.outbox) == 1
        assert 'Test mail' in str(mailer.outbox[0].to_message())
