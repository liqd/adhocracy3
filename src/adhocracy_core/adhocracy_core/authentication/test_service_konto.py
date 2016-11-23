"""Test service konto module."""
from unittest.mock import Mock
from pyramid import testing
from pytest import fixture
from pytest import raises


class TestGetUserDataXml:

    @fixture
    def config(self, config):
        config.registry.settings['adhocracy.service_konto.api_url'] = \
            'http://foo/bar.asmx?wsdl'
        return config

    @fixture
    def mock_user_data(self, mocker):
        from .service_konto import SERVICE_KONTO_GET_USER_DATA_SUCCESS
        mock_user_data = mocker.Mock()
        mock_user_data.GetUserDataResult = SERVICE_KONTO_GET_USER_DATA_SUCCESS
        return mock_user_data

    @fixture
    def mock_osa(self, mocker, mock_user_data):
        mock_osa = mocker.Mock()
        mock_osa.service = Mock()
        mock_osa.service.GetUserData.return_value = \
            mock_user_data
        return mocker.patch(
            'adhocracy_core.authentication.service_konto.osa.Client',
            return_value=mock_osa)

    def call_fut(self, *args):
        from .service_konto import _get_service_konto_user_data_xml
        return _get_service_konto_user_data_xml(*args)

    def test_raise_if_connection_failed(self, registry, config, mock_user_data,
                                        mock_osa, mocker):
        mock_osa.side_effect = AttributeError()
        with raises(ValueError):
            self.call_fut(registry, 'valid')

    def test_raise_if_invalid_token(self, registry, config, mock_user_data,
                                    mock_osa):
        mock_user_data.GetUserDataResult = 123
        with raises(ValueError):
            self.call_fut(registry, 'invalid')

    def test_valid_token(self, registry, config, mock_user_data, mock_osa):
        mock_user_data.strXMLUserData = '<xml/>'
        result = self.call_fut(registry, 'valid')
        mock_osa.assert_called_with('http://foo/bar.asmx?wsdl')
        assert result == '<xml/>'


class TestParseUserDataXml:

    def call_fut(self, *args):
        from .service_konto import _parse_user_data_xml
        return _parse_user_data_xml(*args)

    def test_raise_empty(self):
        from lxml.etree import XMLSyntaxError
        with raises(XMLSyntaxError):
            self.call_fut('')

    def test_raise_invalid_xml(self):
        from lxml.etree import XMLSyntaxError
        with raises(XMLSyntaxError):
            self.call_fut('<USERDATA><HHGW USERID="1" </USERDATA>')

    def test_raise_missing_hhgw(self):
        from lxml.etree import XMLSyntaxError
        with raises(ValueError):
            self.call_fut('<USERDATA><AUTHENTICATION/></USERDATA>')

    def test_raise_incomplete_userdata(self):
        from lxml.etree import XMLSyntaxError
        with raises(ValueError):
            user_data = self.call_fut(
                '<USERDATA>'
                '<HHGW USERID="1" MODEID="1" USERMODE="Bürger" '
                'LOGINNAME="user@foo.bar" TITLE="" PREFIX="Frau" '
                'FIRSTNAME="Foo" LASTNAME="Bar" '
                'LANGUAGE="de-DE" LEVELID="1" STREET="" STREETNUMBER="" '
                'STREETEXTENSION="" CITY="" ZIPCODE="" COUNTRY="Deutschland" '
                'DATEOFBIRTH="" CERTIFICATEID="" USERPHONENUMBER="" />'
                '<ROLES ROLEID="991" ROLENAME="Standard" PERMISSION="1" '
                'ISDEFAULT="1" />'
                '<AUTHENTICATION AuthenticationModeID="1" '
                'InvalidAt="2016-11-08T16:20:03.833" />'
                '</USERDATA>')

    def test_parse_valid(self):
        user_data = self.call_fut(
                '<USERDATA>'
                '<HHGW USERID="1" MODEID="1" USERMODE="Bürger" '
                'LOGINNAME="user@foo.bar" TITLE="" PREFIX="Frau" '
                'FIRSTNAME="Foo" LASTNAME="Bar" EMAIL="user@foo.bar" '
                'LANGUAGE="de-DE" LEVELID="1" STREET="" STREETNUMBER="" '
                'STREETEXTENSION="" CITY="" ZIPCODE="" COUNTRY="Deutschland" '
                'DATEOFBIRTH="" CERTIFICATEID="" USERPHONENUMBER="" />'
                '<ROLES ROLEID="991" ROLENAME="Standard" PERMISSION="1" '
                'ISDEFAULT="1" />'
                '<AUTHENTICATION AuthenticationModeID="1" '
                'InvalidAt="2016-11-08T16:20:03.833" />'
                '</USERDATA>')
        assert user_data.get('userid') == '1'
        assert user_data.get('firstname') == 'Foo'
        assert user_data.get('lastname') == 'Bar'
        assert user_data.get('email') == 'user@foo.bar'


class TestGetUser:

    @fixture
    def mock_locator(self, mocker):
        return mocker.Mock()

    @fixture
    def registry(self, mocker, registry, mock_locator):
        registry.getMultiAdapter = mocker.Mock(return_value=mock_locator)
        return registry

    def call_fut(self, *args):
        from .service_konto import _get_user
        return _get_user(*args)

    def test_search(self, context, registry, request_, mock_locator):
        self.call_fut(context, registry, request_, '1')
        mock_locator.get_user_by_service_konto_userid.assert_called_with('1')


class TestGenerateUserName:

    @fixture
    def mock_locator(self, mocker):
        return mocker.Mock()

    @fixture
    def registry(self, mocker, registry, mock_locator):
        registry.getMultiAdapter = mocker.Mock(return_value=mock_locator)
        return registry

    def call_fut(self, *args):
        from .service_konto import _generate_username
        return _generate_username(*args)

    def test_not_exist(self, context, registry, request_, mock_locator):
        mock_locator.get_user_by_login.return_value = None
        user_data = {'firstname': 'Foo', 'lastname': 'Bar'}
        result = self.call_fut(context, registry, request_, user_data)
        assert result == 'Foo Bar'

    def test_one_exit(self, context, registry, request_, mock_locator):
        user = testing.DummyResource()
        mock_locator.get_user_by_login.side_effect = [user, None]
        user_data = {'firstname': 'Foo', 'lastname': 'Bar'}
        result = self.call_fut(context, registry, request_, user_data)
        assert result == 'Foo Bar 1'

    def test_two_exit(self, context, registry, request_, mock_locator):
        user = testing.DummyResource()
        mock_locator.get_user_by_login.side_effect = [user, user, None]
        user_data = {'firstname': 'Foo', 'lastname': 'Bar'}
        result = self.call_fut(context, registry, request_, user_data)
        assert result == 'Foo Bar 2'


class TestCreateUser:

    @fixture
    def mock_locator(self, mocker):
        return mocker.Mock()

    @fixture
    def registry(self, mocker, registry_with_content, mock_locator):
        registry_with_content.getMultiAdapter = mocker.Mock(return_value=mock_locator)
        return registry_with_content

    @fixture
    def mock_generate_username(self, mocker):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto._generate_username')

    @fixture
    def mock_user_data(self, mocker):
        return {'userid': '1', 'firstname': 'Foo',
                'lastname': 'Bar', 'email': 'foo@bar.com'}

    @fixture
    def mock_user_service(self, mocker):
        user_service = mocker.Mock()
        mocker.patch(
            'adhocracy_core.authentication.service_konto.find_service',
            return_value=user_service)
        return  user_service

    def call_fut(self, *args):
        from .service_konto import _create_user
        return _create_user(*args)

    def test_create_raise_if_email_used(self, context, registry, request_,
                                        mock_locator, mock_user_data):
        mock_locator.get_user_by_email.return_value = testing.DummyResource()
        with raises(ValueError):
            self.call_fut(context, registry, request_, mock_user_data)

    def test_create_user(self, context, registry, request_, mock_locator,
                         mock_generate_username, mock_user_service,
                         mock_user_data):
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets import principal
        mock_locator.get_user_by_email.return_value = None
        mock_generate_username.return_value = 'Foo Bar'
        self.call_fut(context, registry, request_, mock_user_data)
        expected_appstruct = {
            principal.IUserBasic.__identifier__: {'name': 'Foo Bar'},
            principal.IUserExtended.__identifier__: {'email': 'foo@bar.com'},
            principal.IServiceKonto.__identifier__: {'userid': 1},
            principal.IServiceKontoSettings.__identifier__: {'enabled': True},

        }
        registry.content.create.assert_called_with(
            IUser.__identifier__,
            mock_user_service,
            expected_appstruct,
            registry=registry,
            send_event=False
        )


class TestUpdateUser:

    @fixture
    def mock_locator(self, mocker):
        return mocker.Mock()

    @fixture
    def registry(self, mocker, registry_with_content, mock_locator):
        registry_with_content.getMultiAdapter = mocker.Mock(return_value=mock_locator)
        return registry_with_content

    @fixture
    def mock_user_data(self, mocker):
        return {'userid': '1', 'firstname': 'Foo',
                'lastname': 'Bar', 'email': 'foo@bar.com'}

    @fixture
    def mock_user(self, mocker):
        return mocker.Mock()

    def call_fut(self, *args):
        from .service_konto import _update_user
        return _update_user(*args)

    def test_update_raise_if_email_used(self, mocker, context, registry,
                                        request_, mock_locator, mock_user,
                                        mock_user_data):
        mock_locator.get_user_by_email.return_value = testing.DummyResource()
        mock_user_extended_sheet = mocker.Mock()
        mock_user_extended_sheet.get.return_value = {'email': 'old@bar.com'}
        registry.content.get_sheet.return_value = mock_user_extended_sheet
        with raises(ValueError):
            self.call_fut(context, registry, request_, mock_user,
                          mock_user_data)

    def test_ignore_if_nothing_changed(self, mocker, context, registry,
                                       request_, mock_locator, mock_user_data):
        mock_locator.get_user_by_email.return_value = None
        mock_user_extended_sheet = mocker.Mock()
        mock_user_extended_sheet.get.return_value = {'email': 'foo@bar.com'}
        registry.content.get_sheet.return_value = mock_user_extended_sheet
        user = testing.DummyResource()
        self.call_fut(context, registry, request_, user, mock_user_data)
        mock_user_extended_sheet.set.assert_not_called()

    def test_update_user(self, mocker, context, registry, request_,
                         mock_locator, mock_user_data):
        mock_locator.get_user_by_email.return_value = None
        mock_user_extended_sheet = mocker.Mock()
        mock_user_extended_sheet.get.return_value = {'email': 'old@bar.com'}
        registry.content.get_sheet.return_value = mock_user_extended_sheet
        user = testing.DummyResource()
        self.call_fut(context, registry, request_, user, mock_user_data)
        mock_user_extended_sheet.set.assert_called_with(
            {'email': mock_user_data.get('email')})


class TestAuthenticateUser:

    @fixture
    def mock_user_data_xml(self, mocker):
        return mocker.Mock()

    @fixture
    def mock_get_user_data_xml(self, mocker, mock_user_data_xml):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto.'
            '_get_service_konto_user_data_xml',
            return_value=mock_user_data_xml)

    @fixture
    def mock_user_data(self, mocker):
        return {'userid': '1', 'firstname': 'Foo',
                'lastname': 'Bar', 'email': 'foo@bar.com'}

    @fixture
    def mock_parse_user_data_xml(self, mocker, mock_user_data):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto._parse_user_data_xml',
            return_value=mock_user_data)

    @fixture
    def mock_user(self, mocker):
        return mocker.Mock()

    @fixture
    def mock_get_user(self, mocker):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto._get_user')

    @fixture
    def mock_create_user(self, mocker, mock_user):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto._create_user',
            return_value=mock_user)

    @fixture
    def mock_update_user(self, mocker):
        return mocker.patch(
            'adhocracy_core.authentication.service_konto._update_user')

    def call_fut(self, *args):
        from .service_konto import authenticate_user
        return authenticate_user(*args)

    def test_authenticate_raises_if_disabled(self, context, registry,
                                             request_):
        registry.settings['adhocracy.service_konto.enabled'] = 'false'
        with raises(ValueError):
            self.call_fut(context, registry, request_, '12345')

    def test_authenticate_new_user(self, context, registry, request_,
            mock_user_data_xml, mock_get_user_data_xml, mock_user_data,
            mock_parse_user_data_xml, mock_user, mock_get_user,
            mock_create_user, mock_update_user):
        registry.settings['adhocracy.service_konto.enabled'] = 'true'
        mock_get_user.return_value = None
        user = self.call_fut(context, registry, request_, '12345')
        assert user == mock_user
        mock_get_user_data_xml.assert_called_with(registry, '12345')
        mock_parse_user_data_xml.assert_called_with(mock_user_data_xml)
        mock_get_user.asssert_called_with(context, registry, request_, '1')
        mock_create_user.assert_called_with(context, registry, request_,
                                            mock_user_data)
        mock_update_user.assert_not_called()


    def test_authenticate_existing_user(self, context, registry, request_,
                mock_user_data_xml, mock_get_user_data_xml, mock_user_data,
                mock_parse_user_data_xml, mock_user, mock_get_user,
                mock_create_user, mock_update_user):
        registry.settings['adhocracy.service_konto.enabled'] = 'true'
        mock_get_user.return_value = mock_user
        user = self.call_fut(context, registry, request_, '12345')
        assert user == mock_user
        mock_get_user_data_xml.assert_called_with(registry, '12345')
        mock_parse_user_data_xml.assert_called_with(mock_user_data_xml)
        mock_get_user.asssert_called_with(context, registry, request_, '1')
        mock_update_user.assert_called_with(context, registry, request_,
                                            mock_user, mock_user_data)
        mock_create_user.assert_not_called()
