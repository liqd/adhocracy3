"""Messaging support."""
from collections.abc import Sequence

from pkg_resources import resource_exists
from pyramid.registry import Registry
from pyramid.renderers import render
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Message


def send_mail(registry: Registry,
              subject: str,
              recipients: Sequence,
              sender: str=None,
              body: str=None,
              html: str=None):
    """Send a mail message to a list of recipients.

    :param registry: used to retrieve the mailer
    :param subject: the subject of the message
    :param recipients: non-empty list of the email addresses of recipients
    :param sender: the email message of the sender; if None, the configured
        default sender address will be used
    :param body: the plain text body of the message, may be omitted but only if
        ``html`` is given
    :param html: body: the HTML body of the message, may be omitted but only if
        ``body`` is given
    :raise ValueError: if ``recipients`` is empty or if both ``body`` and
        ``html`` are missing or empty
    """
    if not recipients:
        raise ValueError('Empty list of recipients')
    if not (body or html):
        raise ValueError('Email has neither body nor html')
    mailer = _get_mailer(registry)
    message = Message(subject=subject,
                      sender=sender,
                      recipients=recipients,
                      body=body,
                      html=html)
    mailer.send_immediately(message)


def _get_mailer(registry: Registry) -> IMailer:
    return registry.getUtility(IMailer)


def render_and_send_mail(registry: Registry,
                         subject: str,
                         recipients: Sequence,
                         template_asset_base: str,
                         args: dict={},
                         sender: str=None):
    """Render a message from a template and send it as mail.

    The message can contain just a plain text part, an HTML part, or both,
    depending on the templates provided. For example, if you set
    ``template_asset_base`` to 'adhocracy_core:templates/sample', the file
    'adhocracy_core:templates/sample.txt.mako' (if it exists) will be used to
    render the plain text view, and 'adhocracy_core:templates/sample.html.mako'
    (if it exists) will be used to render the HTML view. If neither file
    exists, a ValueError is thrown.

    Template files are parsed by `Mako <http://www.makotemplates.org/>`, see
    `Mako Syntax <http://docs.makotemplates.org/en/latest/syntax.html>`.

    :param registry: used to retrieve the mailer
    :param subject: the subject of the message
    :param recipients: non-empty list of the email addresses of recipients
    :param template_asset_base: the base name of template file(s) to use,
        in format: ``packagename:path/to/file``
    :param args: dictionary or arguments to pass to the renderer
    :param sender: the email message of the sender; if None, the configured
        default sender address will be used
    """
    package, path = template_asset_base.split(':', 1)
    if resource_exists(package, path + '.txt.mako'):
        body = render(template_asset_base + '.txt.mako', args, None)
    else:
        body = None
    if resource_exists(package, path + '.html.mako'):
        html = render(template_asset_base + '.html.mako', args, None)
    else:
        html = None
    return send_mail(registry=registry,
                     subject=subject,
                     recipients=recipients,
                     sender=sender,
                     body=body,
                     html=html)
