"""Service konto module."""
import osa
from lxml import etree
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.settings import asbool
from substanced.interfaces import IUserLocator
from substanced.util import find_service
from adhocracy_core.interfaces import IResource
from adhocracy_core.resources.principal import IUser
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.principal import IServiceKonto


SERVICE_KONTO_GET_USER_DATA_SUCCESS = 1


def authenticate_user(context: IResource, registry: Registry, request: Request,
                      token: str) -> IUser:
    """Authenticate ServiceKonto user.

    Create the user if not yet existing. Update user data.
    Returns:
        user for ServiceKonto account
    """
    service_konto_enabled = asbool(registry.settings.get(
        'adhocracy.service_konto.enabled', False))
    if not service_konto_enabled:
        raise ValueError('ServiceKonto authentication disabled.')
    user_data_xml = _get_service_konto_user_data_xml(registry, token)
    user_data = _parse_user_data_xml(user_data_xml)
    user = _get_user(context, registry, request, int(user_data.get('userid')))
    if not user:
        user = _create_user(context, registry, request, user_data)
    else:
        _update_user(context, registry, request, user, user_data)
    return user


def _get_service_konto_user_data_xml(registry: Registry, token: str) -> str:
    service_konto_url = registry.settings.get(
        'adhocracy.service_konto.api_url')
    try:
        service_konto = osa.Client(service_konto_url)
    except AttributeError:
        raise ValueError('Failed connecting to ServiceKonto.')
    result = service_konto.service.GetUserData(token)
    if not result.GetUserDataResult == SERVICE_KONTO_GET_USER_DATA_SUCCESS:
        raise ValueError('Failed getting user data (return_code: {}).'
                         .format(result.GetUserDataResult))
    return result.strXMLUserData


def _parse_user_data_xml(xml: str) -> dict:
    root = etree.fromstring(xml)
    hhgw = _get_xml_element(root, 'HHGW')
    if hhgw is None:
        raise ValueError('Invalid data received.')
    user_data = dict()
    required_attributes = ['USERID', 'FIRSTNAME', 'LASTNAME', 'EMAIL']
    for attribute in required_attributes:
        user_data[attribute.lower()] = hhgw.get(attribute)
    if not _is_user_data_valid(user_data):
        raise ValueError('Invalid user data received.')
    return user_data


def _get_xml_element(root: etree.ElementTree, tag: str) -> etree.Element:
    for element in root:
        if element.tag == tag:
            return element
    return None


def _is_user_data_valid(user_data: dict) -> bool:
    is_valid = (user_data.get('userid') and
                user_data.get('firstname') and
                user_data.get('lastname') and
                user_data.get('email'))
    return is_valid


def _get_user(context: IResource, registry: Registry, request: Request,
              userid: int) -> IUser:
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    user = locator.get_user_by_service_konto_userid(userid)
    return user


def _create_user(context: IResource, registry: Registry, request: Request,
                 user_data: dict) -> IUser:
    if _is_email_used(context, registry, request, user_data.get('email')):
        raise ValueError('User with ServiceKonto email already exists.')
    users = find_service(context, 'principals', 'users')
    name = _generate_username(context, registry, request, user_data)
    appstruct = {
        IUserBasic.__identifier__: {'name': name},
        IUserExtended.__identifier__: {'email': user_data.get('email')},
        IServiceKonto.__identifier__: {'userid': int(user_data.get('userid'))},
    }
    user = registry.content.create(IUser.__identifier__, users, appstruct,
                                   registry=registry, send_event=False)
    user.activate()
    return user


def _update_user(context: IResource, registry: Registry, request: Request,
                 user: IUser, user_data: dict) -> IUser:
    email = user_data.get('email')
    user_extended_sheet = registry.content.get_sheet(user, IUserExtended)
    appstruct = user_extended_sheet.get()
    if appstruct.get('email') != email:
        if _is_email_used(context, registry, request, email):
            raise ValueError('User with ServiceKonto email already exists.')
        appstruct['email'] = email
        user_extended_sheet.set(appstruct)


def _is_email_used(context: IResource, registry: Registry, request: Request,
                   email: str) -> bool:
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    user = locator.get_user_by_email(email)
    return bool(user)


def _generate_username(context: IResource, registry: Registry,
                       request: Request, user_data: dict) -> str:
    name = user_data.get('firstname') + ' ' + user_data.get('lastname')
    unique_name = name
    i = 1
    while _is_username_used(context, registry, request, unique_name):
        unique_name = name + ' {}'.format(i)
        i += 1
    return unique_name


def _is_username_used(context: IResource, registry: Registry, request: Request,
                      name: str) -> bool:
    locator = registry.getMultiAdapter((context, request), IUserLocator)
    user = locator.get_user_by_login(name)
    return bool(user)


def includeme(config):
    """Register."""
    config.scan('.service_konto')
