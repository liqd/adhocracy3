"""Messaging support."""
from collections.abc import Sequence

from pyramid.registry import Registry
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
