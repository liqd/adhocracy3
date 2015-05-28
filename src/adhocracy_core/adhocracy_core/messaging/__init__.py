"""Send messages to Principals."""
from collections.abc import Sequence
from logging import getLogger

from pkg_resources import resource_exists
from pyramid.registry import Registry
from pyramid.renderers import render
from pyramid.settings import asbool
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Message
from pyramid.traversal import resource_path
from pyramid.request import Request
from pyramid.threadlocal import get_current_request
from pyramid.i18n import TranslationStringFactory

from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.utils import get_sheet_field

logger = getLogger(__name__)

_ = TranslationStringFactory('adhocracy')


class Messenger:

    """Send messages to other people."""

    def __init__(self, registry: Registry):
        """Create a new instance.

        :param registry: used to retrieve and configure the mailer
        """
        self.registry = registry
        settings = registry.settings
        self.use_mail_queue = asbool(settings.get('adhocracy.use_mail_queue',
                                                  False))
        logger.debug('Messenger will use mail queue: %s', self.use_mail_queue)
        self.abuse_handler_mail = settings.get('adhocracy.abuse_handler_mail')
        self.site_name = settings.get('adhocracy.site_name', 'Adhocracy')
        self.frontend_url = settings.get('adhocracy.frontend_url',
                                         'http://localhost:6551')
        self.mailer = registry.getUtility(IMailer)

    def send_mail(self,
                  subject: str,
                  recipients: Sequence,
                  sender: str=None,
                  body: str=None,
                  html: str=None,
                  request: Request=None,
                  ):
        """Send a mail message to a list of recipients.

        :param subject: the subject of the message
        :param recipients: non-empty list of the email addresses of recipients
        :param sender: the email message of the sender; if None, the configured
            default sender address will be used
        :param body: the plain text body of the message, may be omitted but
            only if ``html`` is given
        :param html: body: the HTML body of the message, may be omitted but
            only if ``body`` is given
        :param request: the current request object, if None
            pyramid.threadlocal.get_current_request is used
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
        request = request or get_current_request()
        if request:  # ease testing
            translate = request.localizer.translate
            subject = subject and translate(subject)
            body = body and translate(body)
            html = html and translate(html)
        message = Message(subject=subject,
                          sender=sender,
                          recipients=recipients,
                          body=body,
                          html=html,
                          )
        debug_msg = 'Sending message "{0}" from {1} to {2} with body:\n{3}'
        logger.debug(debug_msg.format(subject, sender, recipients, body))
        if self.use_mail_queue:
            self.mailer.send_to_queue(message)
        else:
            self.mailer.send_immediately(message)

    def render_and_send_mail(self,
                             subject: str,
                             recipients: Sequence,
                             template_asset_base: str,
                             args: dict={},
                             request: Request=None,
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
        :param args: dictionary of arguments to pass to the renderer
        :param sender: the email message of the sender; if None, the configured
            default sender address will be used
        :param request: the current request object, if None
            pyramid.threadlocal.get_current_request is used
        :raise ConnectionError: if no connection to the configured mail server
            can be established
        :raise smtplib.SMTPException: if the mail cannot be sent because the
            target mail server doesn't exist or rejects the connection
        """
        # TODO Adapt the _resource_exists check to make it work with Pyramid
        # asset overriding, cf.
        # http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/assets.html#overriding-assets
        package, path = template_asset_base.split(':', 1)
        if resource_exists(package, path + '.txt.mako'):
            body = render(template_asset_base + '.txt.mako', args)
        else:
            body = None
        if resource_exists(package, path + '.html.mako'):
            html = render(template_asset_base + '.html.mako', args)
        else:
            html = None
        return self.send_mail(subject=subject,
                              recipients=recipients,
                              sender=sender,
                              body=body,
                              html=html,
                              request=request,
                              )

    def send_abuse_complaint(self, url: str, remark: str,
                             user: IResource=None, request: Request=None):
        """Send an abuse complaint to the preconfigured abuse handler.

        :param url: the frontend URL of the resource considered offensive
        :param remark: explanation provided by the complaining user
        :param user: the complaining user, or `None` if not logged in
        """
        user_name = None
        user_url = None
        if user is not None:
            user_name = self._get_user_name(user)
            user_url = self._get_user_url(user)
        args = {'url': url,
                'remark': remark,
                'user_name': user_name,
                'user_url': user_url}
        subject = _('mail_abuse_complaint_subject',
                    mapping={'site_name': self.site_name},
                    default='[${site_name} Abuse Complaint')
        # FIXME For security reasons, we should check that the url starts
        # with one of the prefixes where frontends are supposed to be running
        self.render_and_send_mail(
            subject=subject,
            recipients=[self.abuse_handler_mail],
            template_asset_base='adhocracy_core:templates/abuse_complaint',
            request=request,
            args=args)

    def send_message_to_user(self,
                             recipient: IResource,
                             title: str,
                             text: str,
                             from_user: IResource,
                             request: Request=None,
                             ):
        """Send a message to a specific user."""
        from_email = self._get_user_email(from_user)
        recipient_email = self._get_user_email(recipient)
        sender_name = self._get_user_name(from_user)
        sender_url = self._get_user_url(from_user)
        mapping = {'site_name': self.site_name,
                   'sender_name': sender_name,
                   'sender_url': sender_url,
                   'title': title,
                   'text': text}
        subject = _('mail_sent_message_to_user_subject',
                    mapping=mapping,
                    default='[${site_name}] Message from ${sender_name}: '
                            '${title}')
        body = _('mail_sent_message_to_user_body_txt',
                 mapping=mapping,
                 default='${text}')
        self.send_mail(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            sender=from_email,
            request=request,
        )

    def _get_user_email(self, user: IResource) -> str:
        return get_sheet_field(user, IUserExtended, 'email', self.registry)

    def _get_user_name(self, user: IResource) -> str:
        return get_sheet_field(user, IUserBasic, 'name', self.registry)

    def _get_user_url(self, user: IResource)-> str:
        sender_path = resource_path(user)
        return '%s/r%s/' % (self.frontend_url, sender_path)

    def send_registration_mail(self, user: IUser, activation_path: str,
                               request: Request=None):
        """Send a registration mail to validate the email of a user account."""
        subject = _('mail_account_verification_subject',
                    mapping={'site_name': self.site_name},
                    default='${site_name}: Account Verification / '
                            'Aktivierung Deines Nutzerkontos')
        body_txt = _('mail_account_verification_body_txt',
                     mapping={'activation_path': activation_path,
                              'frontend_url': self.frontend_url,
                              'name': user.name,
                              'site_name': self.site_name,
                              },
                     default='${activation_path}')
        self.send_mail(subject=subject,
                       recipients=[user.email],
                       body=body_txt,
                       request=request,
                       )


def includeme(config):
    """Add Messenger to registry."""
    config.registry.messenger = Messenger(config.registry)
