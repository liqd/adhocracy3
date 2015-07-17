from pyramid import testing
from pytest import fixture
from testfixtures import LogCapture
import colander


@fixture
def request_(cornice_request):
    return cornice_request


class TestJSONHTTPException:

    @fixture
    def make_one(self, errors, **kwargs):
        from adhocracy_core.rest.exceptions import JSONHTTPException
        return JSONHTTPException(errors, **kwargs)

    def test_create(self):
        from pyramid.httpexceptions import HTTPException
        error_entries = []
        inst = self.make_one(error_entries)
        assert isinstance(inst, HTTPException)
        assert inst.status == '400 Bad Request'
        assert inst.content_type == 'application/json'
        assert inst.json_body == {'status': 'error',
                                  'errors': []}

    def test_add_code_and_title(self):
        error_entries = []
        inst = self.make_one(error_entries, code=402, title='Bad Bad')
        assert inst.status == '402 Bad Bad'

    def test_add_error_entries_to_json_body(self):
        from .exceptions import error_entry
        error_entries = [error_entry('header', 'a', 'b')]
        inst = self.make_one(error_entries)
        assert inst.json_body['errors'] == [{'location': 'header',
                                             'name': 'a',
                                             'description': 'b'}]


class TestHandleErrorX0X_exception:

    def call_fut(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_xox_exception
        return handle_error_xox_exception(error, request)

    def test_render_http_exception(self, request_):
        from pyramid.httpexceptions import HTTPClientError
        error = HTTPClientError(status_code=400)
        json_error = self.call_fut(error, request_)
        assert json_error.status_code == 400
        assert json_error.json_body == {"status": "error",
                                        "errors": [{"description": str(error),
                                                    "name": "GET",
                                                    "location": "url"}]}

    def test_render_http_json_exception(self, request_):
        from .exceptions import JSONHTTPException
        error = JSONHTTPException([], code=400)
        json_error = self.call_fut(error, request_)
        assert json_error is error


class TestHandleError400ColanderInvalid:

    def make_one(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_400_colander_invalid
        return handle_error_400_colander_invalid(error, request)

    def test_render_exception_error(self, request_):
        import json
        invalid0 = colander.SchemaNode(typ=colander.String(), name='parent0',
                                       msg='msg_parent')
        invalid1 = colander.SchemaNode(typ=colander.String(), name='child1')
        invalid2 = colander.SchemaNode(typ=colander.String(), name='child2')
        error0 = colander.Invalid(invalid0)
        error1 = colander.Invalid(invalid1)
        error2 = colander.Invalid(invalid2)
        error0.add(error1, 1)
        error1.add(error2, 0)

        inst = self.make_one(error0, request_)

        assert inst.status == '400 Bad Request'
        wanted = {'status': 'error',
                  'errors': [{'location': 'body',
                              'name': 'parent0.child1.child2',
                              'description': ''}]}
        assert json.loads(inst.body.decode()) == wanted


class TestHandleError400URLDecodeError:

    def make_one(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_400_url_decode_error
        return handle_error_400_url_decode_error(error, request)

    def test_render_exception_error(self, request_):
        from pyramid.exceptions import URLDecodeError
        import json
        try:
            b'\222'.decode()
            assert False
        except UnicodeDecodeError as err:
            error = URLDecodeError(err.encoding, err.object,
                                   err.start,err.end, err.reason)
            inst = self.make_one(error, request_)

            assert inst.status == '400 Bad Request'
            wanted = {'status': 'error',
                      'errors': [{'location': 'url',
                                  'name': '',
                                  'description': "'utf-8' codec can't decode byte 0x92 in position 0: invalid start byte"}]}
            assert json.loads(inst.body.decode()) == wanted


class TestHandleError500Exception:

    def make_one(self, error, request_):
        from adhocracy_core.rest.exceptions import handle_error_500_exception
        return handle_error_500_exception(error, request_)

    def test_render_exception_error(self, request_):
        import json
        with LogCapture() as log:
            error = Exception('arg1')
            inst = self.make_one(error, request_)
        assert inst.status == '500 Internal Server Error'
        message = json.loads(inst.body.decode())
        assert message['status'] == 'error'
        assert len(message['errors']) == 1
        assert message['errors'][0]['description'].startswith(
            'Exception: arg1; time: ')
        assert message['errors'][0]['location'] == 'internal'
        assert message['errors'][0]['name'] == ''


class TestHandleAutoUpdateNoForkAllowed400Exception:

    def make_one(self, error, request_):
        from adhocracy_core.rest.exceptions import \
            handle_error_400_auto_update_no_fork_allowed
        return handle_error_400_auto_update_no_fork_allowed(error, request_)

    def test_render_exception_error(self, request_):
        from cornice.util import _JSONError
        from adhocracy_core.interfaces import ISheet
        resource = testing.DummyResource(__name__='resource')
        event = testing.DummyResource(object=resource,
                                      isheet=ISheet,
                                      isheet_field='elements',
                                      new_version=testing.DummyResource(__name__='referenced_new_version'),
                                      old_version=testing.DummyResource(__name__='referenced_old_version'))
        error = testing.DummyResource(resource=resource,
                                      event=event)
        inst = self.make_one(error, request_)
        assert inst.status == '400 Bad Request'
        wanted = \
            {'errors': [{'description': 'No fork allowed - The auto update tried to '
                                        'create a fork for: resource caused by isheet: '
                                        'adhocracy_core.interfaces.ISheet field: '
                                        'elements with old_reference: '
                                        'referenced_old_version and new reference: '
                                        'referenced_new_version. Try another root_version.',
                         'location': 'body',
                         'name': 'root_versions'}],
             'status': 'error'}
        assert inst.json == wanted


class TestHandleError410:

    @fixture
    def error(self):
        from pyramid.httpexceptions import HTTPGone
        return HTTPGone()

    def make_one(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_410_exception
        return handle_error_410_exception(error, request)

    def test_no_detail_no_imetadata(self, error, request_):
        inst = self.make_one(error, request_)
        assert inst.content_type == 'application/json'
        assert inst.json_body['modification_date'] == ''
        assert inst.json_body['modified_by'] is None
        assert inst.json_body['reason'] == ''

    def test_with_detail_no_imetadata(self, error, request_):
        error.detail = 'hidden'
        inst = self.make_one(error, request_)
        assert inst.json_body['reason'] == 'hidden'

    def test_with_detail_and_imetadata(self, error, request_, mock_sheet,
                                       registry_with_content):
        from datetime import datetime
        from adhocracy_core.testing import register_sheet
        from adhocracy_core.sheets.metadata import IMetadata
        resource = testing.DummyResource(__provides__=[IMetadata])
        user = testing.DummyResource(__name__='/user')
        mock_sheet.meta = mock_sheet.meta._replace(isheet=IMetadata)
        mock_sheet.get.return_value = {'modification_date': datetime.today(),
                                       'modified_by': user}
        register_sheet(resource, mock_sheet, registry_with_content)
        error.detail = 'hidden'
        request_.context = resource
        inst = self.make_one(error, request_)
        assert inst.json_body['modification_date'].endswith('00:00')
        assert inst.json_body['modified_by'].endswith('user/')


class TestHandleError400:

    @fixture
    def error(self):
        from pyramid.httpexceptions import HTTPBadRequest
        return HTTPBadRequest()

    def call_fut(self, error, request):
        from .exceptions import handle_error_400_bad_request
        return handle_error_400_bad_request(error, request)

    def test_return_json_error_with_error_listing(self, error, request_):
        request_.errors = [{'location': 'body'}]
        inst = self.call_fut(error, request_)
        assert inst.content_type == 'application/json'
        assert b'"errors": [{"location": "body"}]' in inst.body
        assert b'"status": "error"' in inst.body
        assert inst.status_code == 400

    def test_log_request_body(self, error, request_):
        request_.body = '{"data": "stuff"}'
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert '{"data": "stuff"}' in log_message

    def test_log_abbrivated_request_body_if_gt_5000(self, error, request_):
        request_.body = '{"data": "' + 'h' * 5090 + '"}'
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert len(log_message) < len(request_.body)
            assert '...' in log_message

    def test_log_ignore_if_request_body_is_not_json(
            self, error, request_):
        request_.body = b'wrong'
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert 'wrong' not in log_message

    def test_log_ignore_if_request_body_is_not_json_dict(
            self, error, request_):
        request_.body = '["wrong"]'
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert 'wrong' not in log_message

    def test_log_abbreviated_formdata_body_if_gt_210(self, error, request_):
        request_.content_type = 'multipart/form-data'
        request_.body = "h" * 210
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert len(log_message) < len(request_.body)
            assert log_message.endswith('h...\n')

    def test_log_formdata_body(self, error, request_):
        request_.content_type = 'multipart/form-data'
        request_.body = "h" * 120
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert log_message.endswith('h\n')

    def test_log_but_hide_login_password_in_body(self, error, request_):
        import json
        from .views import POSTLoginUsernameRequestSchema
        appstruct = POSTLoginUsernameRequestSchema().serialize(
            {'password': 'secret', 'name': 'name'})
        request_.body = json.dumps(appstruct)
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert 'secret' not in log_message
            assert '<hidden>' in log_message

    def test_log_but_hide_user_passwod_sheet_password_in_body(self, error,
                                                              request_):
        import json
        from adhocracy_core.sheets.principal import IPasswordAuthentication
        appstruct = {'data': {IPasswordAuthentication.__identifier__:
                                  {'password': 'secret'}}}
        request_.body = json.dumps(appstruct)
        with LogCapture() as log:
            self.call_fut(error, request_)
            log_message = str(log)
            assert 'secret' not in log_message
            assert '<hidden>' in log_message


class TestHandleError403Exception:

    def call_fut(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_403_exception
        return handle_error_403_exception(error, request)

    def test_render_http_exception(self, request_):
        from pyramid.httpexceptions import HTTPClientError
        error = HTTPClientError(status_code=403)
        json_error = self.call_fut(error, request_)
        assert json_error.status_code == 403
        assert json_error.json_body == {"status": "error",
                                        "errors": [{"description": str(error),
                                                    "name": "GET",
                                                    "location": "url"}]}


class TestHandleError410Exception:

    def call_fut(self, error, request):
        from adhocracy_core.rest.exceptions import handle_error_404_exception
        return handle_error_404_exception(error, request)

    def test_render_http_exception(self, request_):
        from pyramid.httpexceptions import HTTPClientError
        error = HTTPClientError(status_code=404)
        json_error = self.call_fut(error, request_)
        assert json_error.status_code == 404
        assert json_error.json_body == {"status": "error",
                                        "errors": [{"description": str(error),
                                                    "name": "GET",
                                                    "location": "url"}]}
