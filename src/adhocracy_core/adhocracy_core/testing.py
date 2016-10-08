"""Public py.test fixtures: http://pytest.org/latest/fixture.html."""
from copy import copy
from functools import partial
from unittest.mock import Mock
from configparser import ConfigParser
from distutils import dir_util
from shutil import rmtree
from subprocess import CalledProcessError
import json
import os
import subprocess
import time

from pyramid.config import Configurator
from pyramid import testing
from pyramid.util import DottedNameResolver
from pyramid.router import Router
from pyramid.scripting import get_root
from pyramid_mailer.mailer import DummyMailer
from pytest import fixture
from testfixtures import LogCapture
from webtest import TestApp
from webtest import TestResponse
from zope.interface.interfaces import IInterface
import transaction

from adhocracy_core.authentication import UserTokenHeader
from adhocracy_core.interfaces import Activity
from adhocracy_core.interfaces import SheetMetadata
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import ResourceMetadata
from adhocracy_core.interfaces import SearchResult
from adhocracy_core.interfaces import SearchQuery
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.resources.root import IRootPool
from adhocracy_core.schema import MappingSchema
from adhocracy_core.scripts import import_resources
from adhocracy_core.scripts import import_local_roles
from adhocracy_core.scripts import import_fixture


#####################################
# Integration/Function test helper  #
#####################################


broken_header = {'X-User-Path': '/principals/users/0000001',
                 'X-User-Token': ''}

batch_url = '/batch'


class DummyPool(testing.DummyResource):
    """Dummy Pool based on :class:`pyramid.testing.DummyResource`."""

    def add(self, name, resource, **kwargs):
        """Add resource to the pool."""
        self[name] = resource
        resource.__parent__ = self
        resource.__name__ = name

    def next_name(self, obj, prefix=''):
        """Get the next name for the resource when using autonaming."""
        return prefix + '_0000000'

    def add_service(self, name, resource, **kwargs):
        """Add a service to the pool."""
        from adhocracy_core.interfaces import IServicePool
        from zope.interface import alsoProvides
        alsoProvides(resource, IServicePool)
        resource.__is_service__ = True
        self.add(name, resource)

    def find_service(self, service_name, *sub_service_names):
        """Return a service from the pool."""
        from substanced.util import find_service
        return find_service(self, service_name, *sub_service_names)

    def remove(self, name, registry=None, send_events=False, **kwargs):
        subresource = self[name]
        del self[name]
        subresource.__name__ = None
        subresource.__parent__ = None


def register_sheet(context, mock_sheet, registry, isheet=None) -> Mock:
    """Register `mock_sheet` for `context`. You can ony use this only once.

    If you need to register multiple mock_sheets in you test add side effects:
    `registry.content.get_sheet.side_effect = [sheet1, sheet2]`.
    You can also set single sheets directly:
    `registry.content.get_sheet.return_value = sheet1
    """
    from zope.interface import alsoProvides
    if isheet is not None:
        mock_sheet.meta = mock_sheet.meta._replace(isheet=isheet)
    if context is not None:
        alsoProvides(context, mock_sheet.meta.isheet)
    registry.content.get_sheet.return_value = mock_sheet
    return mock_sheet


def create_event_listener(config: Configurator, ievent: IInterface) -> list:
    """Register dummy event listener that adds events to the returned List."""
    events = []
    config.add_subscriber(lambda event: events.append(event), ievent)
    return events


##################
# Fixtures       #
##################


@fixture
def pool_graph(integration):
    """Return pool with graph for integration/functional tests."""
    from adhocracy_core.resources.pool import Pool
    from adhocracy_core.resources.root import _add_graph
    from adhocracy_core.resources.root import _add_objectmap_to_app_root
    from adhocracy_core.sheets.pool import IPool
    from zope.interface import directlyProvides
    pool = Pool()
    directlyProvides(pool, IPool)
    _add_objectmap_to_app_root(pool)
    _add_graph(pool, integration.registry)
    return pool


@fixture
def pool_with_catalogs(integration, pool_graph):
    """Return pool with graph and catalog for integration/functional tests."""
    from substanced.interfaces import MODE_IMMEDIATE
    from adhocracy_core.resources.root import _add_catalog_service
    context = pool_graph
    _add_catalog_service(context, integration.registry)
    context['catalogs']['system']['name'].action_mode = MODE_IMMEDIATE
    context['catalogs']['system']['interfaces'].action_mode = MODE_IMMEDIATE
    context['catalogs']['adhocracy']['tag'].action_mode = MODE_IMMEDIATE
    context['catalogs']['adhocracy']['rate'].action_mode = MODE_IMMEDIATE
    return context


@fixture
def integration(config) -> Configurator:
    """Include basic resource types and sheets."""
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.authorization')
    config.include('adhocracy_core.renderers')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources')
    config.include('adhocracy_core.workflows')
    return config


@fixture
def resource_meta() -> ResourceMetadata:
    """Return basic resource metadata."""
    from adhocracy_core.resources import resource_meta
    from adhocracy_core.interfaces import IResource
    return resource_meta._replace(iresource=IResource)


@fixture
def sheet_meta() -> SheetMetadata:
    """Return basic sheet metadata."""
    from adhocracy_core.sheets import sheet_meta
    from adhocracy_core.interfaces import ISheet
    return sheet_meta._replace(isheet=ISheet,
                               schema_class=MappingSchema)


class DummyRequest(testing.DummyRequest):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validated = {}
        self.errors = []
        self.content_type = 'application/json'
        self.text = ''
        self.remote_addr = ''

    def authenticated_userid(self):
        return None

    @property
    def json_body(self):
        return json.loads(self.body)


@fixture
def log(request) -> LogCapture:
    """Return object capturing all log messages."""
    log = LogCapture()

    def fin():
        log.uninstall()
    request.addfinalizer(fin)
    return log


@fixture
def request_(registry):
    """Return dummy request with additional validation attributes.

    Additional Attributes:
        `errors`, `validated`
    """
    request = DummyRequest()
    request.registry = registry
    request.user = None
    request.anonymized_user = None
    request.scheme = 'http'
    request.matched_route = None
    return request


@fixture
def changelog_meta() -> ChangelogMetadata:
    """Return changelog metadata."""
    from adhocracy_core.changelog import changelog_meta
    return changelog_meta


@fixture
def activity() -> Activity:
    """Return activity entry from auditlog."""
    return Activity()


@fixture
def context() -> testing.DummyResource:
    """Return dummy context with IResource interface."""
    from adhocracy_core.interfaces import IResource
    return testing.DummyResource(__provides__=IResource)


@fixture
def pool() -> DummyPool:
    """Return dummy pool with IPool interface."""
    from adhocracy_core.interfaces import IPool
    from substanced.interfaces import IFolder
    return DummyPool(__provides__=(IPool, IFolder))


@fixture
def service() -> DummyPool:
    """Return dummy pool with IServicePool interface."""
    from adhocracy_core.interfaces import IServicePool
    from substanced.interfaces import IFolder
    return DummyPool(__provides__=(IServicePool, IFolder),
                     __is_service__=True)


@fixture
def item() -> DummyPool:
    """Return dummy pool with IItem and IMetadata interface."""
    from adhocracy_core.interfaces import IItem
    from adhocracy_core.sheets.metadata import IMetadata
    return DummyPool(__provides__=(IItem, IMetadata))


@fixture
def version() -> IItemVersion:
    """Return resource with IItemVersion interface."""
    return testing.DummyResource(__provides__=IItemVersion)


@fixture
def node() -> MappingSchema:
    """Return dummy node."""
    return MappingSchema()


@fixture
def changelog(changelog_meta) -> dict:
    """Return transaction_changelog dictionary."""
    from collections import defaultdict
    return defaultdict(lambda: changelog_meta)


@fixture
def registry_with_changelog(registry, changelog):
    """Return registry with transaction_changelog."""
    registry.changelog = changelog
    return registry


@fixture
def mock_sheet() -> Mock:
    """Mock :class:`adhocracy_core.sheets.GenericResourceSheet`."""
    from adhocracy_core.sheets import sheet_meta
    from adhocracy_core.interfaces import ISheet
    # Better would be spec=GenericResourceSheet for the mock object;
    # however this fails if the object is deepcopied.
    sheet = Mock()
    sheet.meta = sheet_meta._replace(isheet=ISheet,
                                     schema_class=MappingSchema)
    sheet.schema = MappingSchema()
    sheet.get.return_value = {}
    return sheet


@fixture
def mock_graph() -> Mock:
    """Mock :class:`adhocracy_core.graph.Graph`."""
    from adhocracy_core.graph import Graph
    mock = Mock(spec=Graph)
    return mock


@fixture
def mock_catalogs(search_result) -> Mock:
    """Mock :class:`adhocracy_core.catalogs.ICatalalogsService`."""
    from zope.interface import alsoProvides
    from adhocracy_core.interfaces import IServicePool
    from adhocracy_core.catalog import CatalogsServiceAdhocracy
    catalogs = testing.DummyResource()
    alsoProvides(catalogs, IServicePool)
    search_mock = Mock(spec=CatalogsServiceAdhocracy.search)
    search_mock.return_value = search_result
    catalogs.search = search_mock
    reindex_index_mock = Mock(spec=CatalogsServiceAdhocracy.reindex_index)
    catalogs.reindex_index = reindex_index_mock
    get_index_mock = Mock(spec=CatalogsServiceAdhocracy.get_index)
    catalogs.get_index = get_index_mock
    return catalogs


@fixture
def search_result() -> SearchResult:
    """Return search result."""
    from adhocracy_core.interfaces import search_result
    return search_result._replace(elements=[])


@fixture
def query() -> SearchQuery:
    """Return search query."""
    from adhocracy_core.interfaces import search_query
    return search_query


@fixture
def sheet_catalogs(monkeypatch, mock_catalogs) -> Mock:
    """Mock _catalogs property for sheets."""
    from adhocracy_core import sheets
    monkeypatch.setattr(sheets, 'find_service', lambda x, y: mock_catalogs)
    return mock_catalogs


@fixture
def mock_objectmap() -> Mock:
    """Mock :class:`substanced.objectmap.ObjectMap`."""
    from substanced.objectmap import ObjectMap
    mock = Mock(spec=ObjectMap)
    mock.get_reftypes.return_value = []
    return mock


@fixture
def mock_workflow() -> Mock:
    """Mock :class:`adhocracy_core.workflows.AdhocracyACLWorkflow`."""
    from adhocracy_core.workflows import ACLLocalRolesWorkflow
    mock = Mock(spec=ACLLocalRolesWorkflow)
    mock._states = {}
    mock.get_next_states.return_value = []
    mock.state_of.return_value = None
    mock.type = 'sample'
    mock._initial_state = 'draft'
    return mock


@fixture
def mock_content_registry() -> Mock:
    """Mock :class:`adhocracy_core.content.ResourceContentRegistry`."""
    from adhocracy_core.content import ResourceContentRegistry
    mock = Mock(spec=ResourceContentRegistry)
    mock.sheets_meta = {}
    mock.resources_meta = {}
    mock.workflows_meta = {}
    mock.workflows = {}
    mock.get_resources_meta_addable.return_value = []
    mock.resources_meta_addable = {}
    mock.get_sheets_read.return_value = []
    mock.get_sheets_edit.return_value = []
    mock.get_sheets_create.return_value = []
    mock.get_sheet.return_value = None
    mock.get_sheet_field = lambda x, y, z: mock.get_sheet(x, y).get()[z]
    mock.can_add_anonymized.return_value = False
    mock.can_edit_anonymized.return_value = False
    mock.can_delete_anonymized.return_value = False
    return mock


@fixture
def registry_with_content(registry, mock_content_registry):
    """Return registry with content registry attribute."""
    registry.content = mock_content_registry
    return registry


@fixture
def config(request) -> Configurator:
    """Return dummy testing configuration."""
    config = testing.setUp()
    config.include('tzf.pyramid_yml')
    config.config_defaults('adhocracy_core:defaults.yaml')
    request.addfinalizer(testing.tearDown)
    return config


@fixture
def registry(config) -> object:
    """Return dummy registry."""
    return config.registry


@fixture
def kw(context, registry, request_) -> dict:
    """Return default keyword arguments for schema binding.

    Available kwargs: request, content, registry, creating

    Note: If the registry keyword is not need, this fixture should not be
          used. This makes the tests run faster and we don't declare needless
          dependencies.
    """
    return {'request': request_,
            'registry': registry,
            'context': context,
            'creating': None,
            }


@fixture
def mock_user_locator(registry) -> Mock:
    """Mock :class:`adhocracy_core.resource.principal.UserLocatorAdapter`."""
    from zope.interface import Interface
    from adhocracy_core.interfaces import IRolesUserLocator
    from adhocracy_core.resources.principal import UserLocatorAdapter
    locator = Mock(spec=UserLocatorAdapter)
    locator.get_groupids.return_value = None
    locator.get_roleids.return_value = None
    locator.get_user_by_userid.return_value = None
    locator.get_user_by_login.return_value = None
    locator.get_user_by_email.return_value = None
    locator.get_group_roleids.return_value = None
    locator.get_role_and_group_roleids.return_value = None
    registry.registerAdapter(lambda y, x: locator, (Interface, Interface),
                             IRolesUserLocator)
    return locator


@fixture
def mock_messenger():
    """Return mock messenger."""
    from adhocracy_core.messaging import Messenger
    messenger = Mock(spec=Messenger)
    return messenger


def _get_settings(request, part):
    """Return settings of a config part."""
    config_parser = ConfigParser()
    config_file = 'etc/test.ini'
    config_parser.read(config_file)
    settings = {}
    for option, value in config_parser.items(part):
        settings[option] = value
    return settings


@fixture(scope='class')
def settings(request) -> dict:
    """Return app:main and server:main settings."""
    settings = {}
    app = _get_settings(request, 'app:main')
    settings.update(app)
    server = _get_settings(request, 'server:main')
    settings.update(server)
    return settings


@fixture(scope='class')
def app_settings(request) -> dict:
    """Return settings to start the test wsgi app."""
    settings = {}
    settings['yaml.location'] = 'adhocracy_core:test_memory.yaml'
    return settings


@fixture(scope='class')
def ws_settings(request) -> Configurator:
    """Return websocket server settings."""
    return _get_settings(request, 'websockets')


@fixture(scope='session')
def supervisor(request) -> str:
    """Start supervisord daemon."""
    pid_file = 'var/supervisord.pid'
    if _is_running(pid_file):
        return True
    try:
        subprocess.check_output('bin/supervisord',
                                shell=True,
                                stderr=subprocess.STDOUT)
    # workaround if pid file is missing but supervisord is still running
    except CalledProcessError as err:
        print(err)


@fixture(scope='class')
def zeo(request, supervisor) -> str:
    """Start zeo server with supervisor."""
    output = subprocess.check_output(
        'bin/supervisorctl restart adhocracy_test:test_zeo',
        shell=True,
        stderr=subprocess.STDOUT)

    def fin():
        subprocess.check_output(
            'bin/supervisorctl stop adhocracy_test:test_zeo',
            shell=True,
            stderr=subprocess.STDOUT)
        subprocess.check_output('rm -rf var/db/test/Data.fs*',
                                shell=True,
                                stderr=subprocess.STDOUT)
    request.addfinalizer(fin)
    return output


@fixture(scope='class')
def websocket(request, zeo) -> bool:
    """Start websocket server with supervisor."""
    output = subprocess.check_output(
        'bin/supervisorctl restart adhocracy_test:test_autobahn',
        shell=True,
        stderr=subprocess.STDOUT)

    def fin():
        subprocess.check_output(
            'bin/supervisorctl stop adhocracy_test:test_autobahn',
            shell=True,
            stderr=subprocess.STDOUT)
    request.addfinalizer(fin)

    return output


def _kill_pid_in_file(path_to_pid_file):
    if os.path.isfile(path_to_pid_file):
        pid = open(path_to_pid_file).read().strip()
        pid_int = int(pid)
        os.kill(pid_int, 15)
        time.sleep(1)
        subprocess.call(['rm', path_to_pid_file])


def _is_running(path_to_pid_file) -> bool:
    if os.path.isfile(path_to_pid_file):
        pid = open(path_to_pid_file).read().strip()
        pid_int = int(pid)
        try:
            os.kill(pid_int, 0)
        except OSError:
            subprocess.call(['rm', path_to_pid_file])
        else:
            return True


def add_create_test_users_subscriber(configurator):
    """Register a subscriber to import the test fixture to create users."""
    import_test_fixture = partial(import_fixture,
                                  'adhocracy_core:test_users_fixture',
                                  print_stdout=False)

    configurator.add_subscriber(lambda event:
                                import_test_fixture(event.object,
                                                    event.registry),
                                IResourceCreatedAndAdded,
                                object_iface=IRootPool)


@fixture(scope='class')
def app_router(app_settings) -> Router:
    """Return the adhocracy test wsgi application."""
    import adhocracy_core
    configurator = make_configurator(app_settings, adhocracy_core)
    app_router = configurator.make_wsgi_app()
    return app_router


def make_configurator(app_settings: dict, package) -> Configurator:
    """Make the pyramid configurator."""
    configurator = Configurator(settings=app_settings,
                                root_factory=package.root_factory)
    configurator.include(package)
    add_create_test_users_subscriber(configurator)
    return configurator


@fixture(scope='class')
def app_router_filestorage(app_settings_filestorage: dict) -> Router:
    """Return the adhocracy test wsgi application using file storage db."""
    import adhocracy_core

    configurator = make_configurator(app_settings_filestorage, adhocracy_core)
    app_router = configurator.make_wsgi_app()
    return app_router


@fixture(scope='class')
def app_settings_filestorage(request, app_settings: dict) -> dict:
    """Add zodb connection with filestorage, add finalizer to cleanup files."""
    app_settings['yaml.location'] = 'adhocracy_core:test_persistent.yaml'
    db_test_dir = 'var/db/test/'
    db_file = db_test_dir + 'Data.fs'
    blobs_dir = db_test_dir + 'blobs'

    def remove_test_db():
        os.remove(db_file)
        os.remove(db_file + '.lock')
        os.remove(db_file + '.tmp')
        os.remove(db_file + '.index')
        rmtree(blobs_dir, ignore_errors=True)
    request.addfinalizer(remove_test_db)

    return app_settings


@fixture(scope='class')
def newest_activation_path(app_router):
    """Return the newest activation path generated by app."""
    import re
    mailer = app_router.registry.messenger.mailer
    last_message_body = mailer.outbox[-1].body
    path_match = re.search(r'/activate/\S+', last_message_body)
    return path_match.group()


@fixture(scope='class')
def newest_reset_path(app_router) -> callable:
    """Return callable to get newest reset password path generated by app."""
    from urllib.request import unquote
    mailer = app_router.registry.messenger.mailer

    def get_newest_reset_path():
        last_message_body = mailer.outbox[-1].body
        path_quoted = last_message_body.split('path=')[1].split()[0]
        path = unquote(path_quoted)
        return path
    return get_newest_reset_path


@fixture(scope='class')
def send_mails(app_router) -> list:
    """Return send mails."""
    return app_router.registry.messenger.mailer.outbox


class AppUser:
    """:class:`webtest.TestApp` wrapper for backend functional testing."""

    def __init__(self,
                 app_router: Router,
                 rest_url: str='http://localhost',
                 base_path: str='/',
                 header: dict=None,
                 user_path: str='',
                 user_login: str='',
                 user_password: str='',
                 ):
        """Initialize self."""
        self.app_router = app_router
        """The adhocracy wsgi application"""
        self.app = TestApp(app_router)
        """:class:`webtest.TestApp`to send requests to the backend server."""
        self.rest_url = rest_url
        """backend server url to generate request urls."""
        self.base_path = base_path
        """path prefix to generate request urls."""
        self.header = header or {}
        """default header for requests, mostly for authentication.
           If not set, `user_login` and `user_password` is used to login,
           the new authentication header is stored in `header`.
        """
        if user_password and user_login and not header:
            token, user_path = self._get_token_and_user_path(user_login,
                                                             user_password)
            self.header = {UserTokenHeader: token}
        self.user_password = user_password
        """password for authenticated user."""
        self.user_login = user_login
        """login name for authenticated user."""
        self.user_path = user_path
        """path for authenticated user."""
        self._resolver = DottedNameResolver()

    def _get_token_and_user_path(self, login: str, password: str) -> tuple:
        login_page = self.rest_url + '/login_username'
        data = {'name': login,
                'password': password}
        resp = self.app.post_json(login_page, data).json
        return resp['user_token'], resp['user_path']

    def post_resource(self, path: str,
                      iresource: IInterface,
                      cstruct: dict) -> TestResponse:
        """Build and post request to create a new resource."""
        url = self._build_url(path)
        props = self._build_post_body(iresource, cstruct)
        resp = self.app.post_json(url, props, headers=self.header,
                                  expect_errors=True)
        return resp

    def put(self,
            path: str,
            cstruct: dict={},
            upload_files: [(str, str, bytes)]=None,
            extra_headers: dict={},
            ) -> TestResponse:
        """Put request to modify a resource."""
        url = self._build_url(path)
        headers = copy(self.header)
        headers.update(extra_headers)
        kwargs = {'headers': headers,
                  'expect_errors': True,
                  }
        if upload_files:
            kwargs['upload_files'] = upload_files
            resp = self.app.put(url, cstruct, **kwargs)
        else:
            resp = self.app.put_json(url, cstruct, **kwargs)
        return resp

    def post(self,
             path: str,
             cstruct: dict={},
             upload_files: [(str, str, bytes)]=None,
             extra_headers: dict={},
             ) -> TestResponse:
        """Post request to create a new resource."""
        url = self._build_url(path)
        headers = copy(self.header)
        headers.update(extra_headers)
        kwargs = {'headers': headers,
                  'expect_errors': True,
                  }
        if upload_files:
            kwargs['upload_files'] = upload_files
            resp = self.app.post(url, cstruct, **kwargs)
        else:
            resp = self.app.post_json(url, cstruct, **kwargs)
        return resp

    def _build_post_body(self, iresource: IInterface, cstruct: dict) -> dict:
        return {'content_type': iresource.__identifier__,
                'data': cstruct}

    def _build_url(self, path: str) -> str:
        if path.startswith('http'):
            return path
        return self.rest_url + self.base_path + path

    def batch(self, subrequests: list):
        """Build and post batch request to the backend rest server."""
        resp = self.app.post_json(batch_url, subrequests, headers=self.header,
                                  expect_errors=True)
        return resp

    def get(self, path: str, params={}, extra_headers={}) -> TestResponse:
        """Send get request to the backend rest server."""
        url = self._build_url(path)
        headers = copy(self.header)
        headers.update(extra_headers)
        resp = self.app.get(url,
                            headers=headers,
                            params=params,
                            expect_errors=True)
        return resp

    def delete(self, path: str) -> TestResponse:
        """Send delete request to the backend rest server."""
        url = self._build_url(path)
        resp = self.app.delete(url,
                               headers=self.header,
                               expect_errors=True)
        return resp

    def options(self, path: str) -> TestResponse:
        """Send options request to the backend rest server."""
        url = self._build_url(path)
        resp = self.app.options(url, headers=self.header, expect_errors=True)
        return resp

    def get_postable_types(self, path: str) -> []:
        """Send options request and return the postable content types."""
        resp = self.options(path)
        if 'POST' not in resp.json:
            return []
        post_request_body = resp.json['POST']['request_body']
        type_names = sorted([r['content_type'] for r in post_request_body])
        iresources = [self._resolver.resolve(t) for t in type_names]
        return iresources


@fixture(scope='class')
def app_anonymous(app_router) -> TestApp:
    """Return backend test app wrapper with participant authentication."""
    return AppUser(app_router)


@fixture(scope='class')
def app_broken_token(app_router) -> TestApp:
    """Return backend test app wrapper with participant authentication."""
    return AppUser(app_router, header=broken_header)


@fixture(scope='class')
def app_participant(app_router) -> TestApp:
    """Return backend test app wrapper with participant authentication."""
    return AppUser(app_router,
                   user_login='participant',
                   user_password='password')


@fixture(scope='class')
def app_participant2(app_router) -> TestApp:
    """Return backend test app wrapper with participant authentication."""
    return AppUser(app_router,
                   user_login='participant2',
                   user_password='password')


@fixture(scope='class')
def app_authenticated(app_router) -> TestApp:
    """Return backend test app wrapper with authenticated authentication."""
    return AppUser(app_router,
                   user_login='authenticated',
                   user_password='password')


@fixture(scope='class')
def app_moderator(app_router):
    """Return backend test app wrapper with moderator authentication."""
    return AppUser(app_router,
                   user_login='moderator',
                   user_password='password')


@fixture(scope='class')
def app_initiator(app_router):
    """Return backend test app wrapper with initiator authentication."""
    return AppUser(app_router,
                   user_login='initiator',
                   user_password='password')


@fixture(scope='class')
def app_admin(app_router):
    """Return backend test app wrapper with admin authentication."""
    return AppUser(app_router,
                   user_login='admin',
                   user_password='password')


@fixture(scope='class')
def app_admin_filestorage(app_router_filestorage):
    """Return backend test app wrapper with admin authentication."""
    return AppUser(app_router_filestorage,
                   user_login='admin',
                   user_password='password')


@fixture(scope='class')
def app_god(app_router):
    """Return backend test app wrapper with god authentication."""
    return AppUser(app_router,
                   user_login='god',
                   user_password='password')


@fixture(scope='class')
def global_anonymization_userid(app_router):
    """Return userid of global anonymisation user."""
    return '/principals/users/0000001'


@fixture(scope='class')
def mailer(app_router) -> DummyMailer:
    """Return DummyMailer of `app_router` fixture."""
    mailer = app_router.registry.messenger.mailer
    return mailer


@fixture
def datadir(tmpdir, request):
    """Fixture to access tests data.

    Responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.

    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


def add_resources(app_router: Router, filename: str):
    """Add resources from a JSON file to the app."""
    _run_import_function(import_resources, app_router, filename)


def add_local_roles(app_router: Router, filename: str):
    """Add local roles from a JSON file to resources."""
    _run_import_function(import_local_roles, app_router, filename)


def _run_import_function(func: callable, app_router: Router, filename: str):
    root, closer = get_root(app_router)
    try:
        func(root, app_router.registry, filename)
        transaction.commit()
    finally:
        closer()


def do_transition_to(app_user, path, state) -> TestResponse:
    """Transition to a new workflow state by sending a PUT request."""
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    data = {'data': {IWorkflowAssignment.__identifier__:
                     {'workflow_state': state}}}
    resp = app_user.put(path, data)
    return resp


def get_next_states(app_user, path) -> []:
    """Get possible transitions to new worklfow states."""
    from adhocracy_core.sheets.workflow import IWorkflowAssignment
    resp = app_user.options(path).json
    workflow_datas = [y for x, y in resp['PUT']['request_body']['data'].items()
                      if IWorkflowAssignment.__identifier__ in x]
    workflow_data = workflow_datas and workflow_datas[0] or {}
    return workflow_data.get('workflow_state', [])
