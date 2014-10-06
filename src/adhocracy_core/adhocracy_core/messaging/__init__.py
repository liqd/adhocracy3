"""Messaging support."""
from collections.abc import Sequence

from pkg_resources import resource_exists
from pyramid.registry import Registry
from pyramid.renderers import render
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Message


class Messenger():

    """Send messages to other people."""

    def __init__(self, registry: Registry):
        """Create a new instance.

        :param registry: used to retrieve the mailer
        """
        self.registry = registry

    def send_mail(self,
                  subject: str,
                  recipients: Sequence,
                  sender: str=None,
                  body: str=None,
                  html: str=None):
        """Send a mail message to a list of recipients.

        :param subject: the subject of the message
        :param recipients: non-empty list of the email addresses of recipients
        :param sender: the email message of the sender; if None, the configured
            default sender address will be used
        :param body: the plain text body of the message, may be omitted but
            only if ``html`` is given
        :param html: body: the HTML body of the message, may be omitted but
            only if ``body`` is given
        :raise ValueError: if ``recipients`` is empty or if both ``body`` and
            ``html`` are missing or empty
        :raise ConnectionError: if no connection to the configured mail server
            can be established
        :raise smtplib.SMTPException: if the mail cannot be sent because the
            target mail server doesn't exist or rejects the connection
        """
        if not recipients:
            raise ValueError('Empty list of recipients')
        if not (body or html):
            raise ValueError('Email has neither body nor html')
        mailer = self._get_mailer()
        message = Message(subject=subject,
                          sender=sender,
                          recipients=recipients,
                          body=body,
                          html=html)
        mailer.send_immediately(message)

    def _get_mailer(self) -> IMailer:
        return self.registry.getUtility(IMailer)

    def render_and_send_mail(self,
                             subject: str,
                             recipients: Sequence,
                             template_asset_base: str,
                             args: dict={},
                             sender: str=None):
        """Render a message from a template and send it as mail.

        The message can contain just a plain text part, an HTML part, or both,
        depending on the templates provided. For example, if you set
        ``template_asset_base`` to 'adhocracy_core:templates/sample', the file
        'adhocracy_core:templates/sample.txt.mako' (if it exists) will be used
        to render the plain text view, and
        'adhocracy_core:templates/sample.html.mako' (if it exists) will be
        used to render the HTML view. If neither file exists, a ValueError is
        thrown.

        Template files are parsed by `Mako <http://www.makotemplates.org/>`,
        see
        `Mako Syntax <http://docs.makotemplates.org/en/latest/syntax.html>`.

        :param subject: the subject of the message
        :param recipients: non-empty list of the email addresses of recipients
        :param template_asset_base: the base name of template file(s) to use,
            in format: ``packagename:path/to/file``
        :param args: dictionary or arguments to pass to the renderer
        :param sender: the email message of the sender; if None, the configured
            default sender address will be used
        :raise ConnectionError: if no connection to the configured mail server
            can be established
        :raise smtplib.SMTPException: if the mail cannot be sent because the
            target mail server doesn't exist or rejects the connection
        """
        # FIXME Mails (subjects and template_asset_bases) should be
        # translatable
        # FIXME Adapt the _resource_exists check to make it work with Pyramid
        # asset overriding, cf.
        # http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/assets.html#overriding-assets
        package, path = template_asset_base.split(':', 1)
        if self._resource_exists(package, path + '.txt.mako'):
            body = self._render(template_asset_base + '.txt.mako', args)
        else:
            body = None
        if self._resource_exists(package, path + '.html.mako'):
            html = self._render(template_asset_base + '.html.mako', args)
        else:
            html = None
        return self.send_mail(subject=subject,
                              recipients=recipients,
                              sender=sender,
                              body=body,
                              html=html)

    def _resource_exists(self, package: str, path: str) -> bool:
        return resource_exists(package, path)

    def _render(self, template_name: str, args: dict) -> str:
        return render(template_name, args, None)


def includeme(config):
    """Add Messenger to registry."""
    config.registry.messenger = Messenger(config.registry)
