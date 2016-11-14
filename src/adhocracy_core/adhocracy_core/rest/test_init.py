from pytest import fixture


class TestAPIView:

    def make_one(self, **kwargs):
        from . import api_view
        return api_view(**kwargs)

    @fixture
    def venusian(self):
        from pyramid.tests.test_view import DummyVenusian
        return DummyVenusian()

    def test_create_defaults(self):
        inst = self.make_one()
        assert inst.__dict__ == {}

    def test_create_custom_settings(self):
        inst = self.make_one(permission='foo')
        assert inst.permission == 'foo'

    def test_call_wrap_to_attach_add_view(self, venusian):
        inst = self.make_one()
        inst.venusian = venusian
        def foo(): pass
        wrapped = inst(foo)
        assert wrapped is foo
        assert len(venusian.attachments) == 1
        assert venusian.attachments[0][0] == wrapped
        assert callable(venusian.attachments[0][1])
        assert venusian.attachments[0][2] == 'adhocracy'

    def test_call_defaults(self, venusian):
        from pyramid.tests.test_view import call_venusian
        from adhocracy_core.interfaces import API_ROUTE_NAME
        from adhocracy_core import authentication
        from adhocracy_core import caching
        from . import schemas
        inst = self.make_one()
        inst.venusian = venusian
        def foo(): pass
        wrapped = inst(foo)
        config = call_venusian(venusian)
        assert config.settings ==\
               [{'decorator': [authentication.validate_user_headers,
                               authentication.validate_anonymize_header,
                               authentication.validate_password_header,
                               schemas.validate_visibility,
                               caching.set_cache_header,
                               ],
                'route_name': API_ROUTE_NAME,
                'renderer': 'json',
                'view': None,  # comes from call_venusian
                'venusian': venusian}]

    def test_call_with_schema_setting(self, mocker, venusian):
        from pyramid.tests.test_view import call_venusian
        from colander import Schema
        inst = self.make_one(schema=Schema)
        inst.venusian = venusian
        def foo(): pass
        mock_data_validator = mocker.patch('adhocracy_core.rest.'
                                           'validate_request_data')
        wrapped = inst(foo)
        config = call_venusian(venusian)
        data_validator = config.settings[0]['decorator'][-1]
        mock_data_validator.assert_called_with(Schema)
        assert data_validator == mock_data_validator.return_value

    def test_call_with_custom_settings(self, venusian):
        from pyramid.tests.test_view import call_venusian
        inst = self.make_one(renderer='foo')
        inst.venusian = venusian
        def foo(): pass
        wrapped = inst(foo)
        config = call_venusian(venusian)
        assert config.settings[0]['renderer'] == 'foo'

    def test_call_view_class(self, venusian):
        from pyramid.tests.test_view import call_venusian
        inst = self.make_one()
        inst.venusian = venusian
        inst.venusian.info.scope = 'class'
        class foo(object): pass
        wrapped = inst(foo)
        config = call_venusian(venusian)
        assert config.settings[0]['attr'] == 'foo'

