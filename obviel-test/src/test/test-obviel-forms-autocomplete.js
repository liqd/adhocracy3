/*global buster:false, sinon:false, obviel:false */
var assert = buster.assert;
var console = buster.console;

var testel = function() {
    return $("#viewdiv");
};

var autocompleteTestCase = buster.testCase('autocomplete tests', {
    setUp: function() {
        this.server = sinon.fakeServer.create();
        $('#jsview-area').html('<div id="viewdiv"></div>');
        $('#jsview-area').unbind();
        
        // XXX would be nice to be able to register this centrally
        this.mockJson = function(url, json) {
            var getResponse;
            if ($.isFunction(json)) {
                getResponse = json;
            } else {
                getResponse = function() {
                    return json;
                };
            }
            var response = function(request) {
                request.respond(200, { 'Content-Type': 'application/json'},
                                JSON.stringify(getResponse(request)));
            };
            this.server.respondWith('GET', url, response);
            // XXX also respond to POST
            this.server.respondWith('POST', url, response);
        };
    },
    tearDown: function() {
        this.server.restore();
        $('#jsview-area').unview();
        $('#viewdiv').unbind();
    },

    "autocomplete set values": function () {
        var el= testel();
        var data = {};
        var errors = {};
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'Autocomplete',
                    data: [
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}
                    ],
                    defaultvalue: 'foo'
                }]
            },
            data: data,
            errors: errors
        });

        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('Qux'); // invalid value
        fieldEl.trigger('change');
        assert.equals(errors.a, 'unknown value');
        assert.equals(data.a, 'foo');

        fieldEl.val('Bar');
        fieldEl.trigger('change');
        assert.equals(errors.a, '');
        assert.equals(data.a, 'bar');
    },

    "autocomplete set value with blur": function () {
        var el= testel();
        var data = {};
        var errors = {};
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'Autocomplete',
                    data: [
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}
                    ],
                    defaultvalue: 'foo'
                }]
            },
            data: data,
            errors: errors
        });

        var formEl = $('form', el);
        var fieldEl = $('input[name="obviel-field-cloned-test-a"]', formEl);
        fieldEl.val('Bar');
        fieldEl.trigger('blur');
        assert.equals(errors.a, '');
        assert.equals(data.a, 'bar');
    },

    // would be nice to also test close event but seems difficult to
    // simulate
    
    "autocomplete requiredness": function () {
        var el = testel();
        var data = {};
        var errors = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'Autocomplete',
                    data: [
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}
                    ],
                        validate: {
                            required: true
                        }
                }]
            },
            data: data,
            errors: errors
        });

        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val(''); // empty while it's required
        fieldEl.trigger('change');
        assert.equals(errors.a, 'this field is required');
    },

    "autocomplete with global error": function () {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};
        
        this.mockJson('validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.a === 'wrong') {
                return {'a': 'must not be wrong'};
            }
            return {};
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'A',
                    data: [{value: 'wrong', label: 'Wrong'},
                           {value: 'right', label: 'Right'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });

        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        
        fieldA_el.val('Wrong');
        
        // submitting this should trigger a global error
        var view = el.view();
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, 'must not be wrong');
        
        // it also shows up in the element
        var fieldGlobalA = $('#obviel-global-error-test-a', formEl);
        assert.equals(fieldGlobalA.text(), 'must not be wrong');
        
        // make the global validation problem go away again
        fieldA_el.val('Right');
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, '');
        assert.equals(fieldGlobalA.text(), '');
    },

    "autocomplete url set values": function () {
        var el = testel();
        var data = {};
        var errors = {};

        
        this.server.respondWith(function(request) {
            var params = $.deparam.querystring(request.url);
            var key = params.identifier || params.term || '';
            key = key.toLowerCase();
            if ('foo'.indexOf(key) >= 0) {
                request.respond(
                    200, {'Content-Type': 'application/json'},
                    JSON.stringify([{value: 'foo', label: 'Foo'}]));
            } else if ('bar'.indexOf(key) >= 0) {
                request.respond(
                    200, {'Content-Type': 'applicaton/json'},
                    JSON.stringify([{value: 'bar', label: 'Bar'}]));
            } else if ('qux'.indexOf(key) >= 0) {
                request.respond(
                    200, {'Content-Type': 'application/json'},
                    JSON.stringify([{value: 'qux', label: 'Qux'}]));
            }
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify([]));
        });
        

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'Autocomplete',
                    data: 'testUrl',
                    defaultvalue: 'foo'
                }]
            },
            data: data,
            errors: errors
        });
        this.server.respond();
        
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('Doo'); // invalid value
        fieldEl.trigger('change');
        this.server.respond();
        
        assert.equals(errors.a, 'unknown value');
        assert.equals(data.a, 'foo');

        // cache value for autocomplete
        var view = fieldEl.closest('.obviel-field').view();
        view.source({term: 'Bar'}, function () {});
        this.server.respond();
        view.source({term: 'Qux'}, function () {});
        this.server.respond();
        
        fieldEl.val('Bar');
        fieldEl.trigger('change');
        this.server.respond();
        
        assert.equals(errors.a, '');
        assert.equals(data.a, 'bar');

        $(data).setField('a', 'qux');
        this.server.respond();
        
        assert.equals(fieldEl.val(), 'Qux');

    },
    "autocomplete url http error": function () {
        var el = testel();
        var data = {};
        var errors = {};

        var spy = sinon.spy();
        obviel.httpErrorHook(spy);

        // need to be a general handler because otherwise urls with parameters
        // (which autocomplete generates) won't be handled and the error
        // will be a 404
        this.server.respondWith(function(request) {
            request.respond(500, {'Content-Type': 'text/html'},
                                 '<div>Internal server error</div>');
        });

        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['autocompleteField'],
                    name: 'a',
                    title: 'Autocomplete',
                    data: 'testUrl',
                    defaultvalue: 'foo'
                }]
            },
            data: data,
            errors: errors
        });
        this.server.respond();
        
        assert.calledOnce(spy);
        assert.equals(spy.args[0][0].status, 500);
    }

});
