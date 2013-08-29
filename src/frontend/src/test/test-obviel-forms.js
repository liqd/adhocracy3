/*global obviel:false, buster:false, sinon:false*/

var assert = buster.assert;
var refute = buster.refute;

$.fn.htmlLower = function() {
    // some nasty normalization for IE
    var html = this.html();
    return html.toLowerCase().replace(/"/g, '');
};


// to make data binding work we need a real DOM element,
// and cannot get away with a created element as we can in other places
var testel = function() {
    return $('#viewdiv');
};

var change = function(el) {
    el.trigger('change');
};

obviel.iface('successIface');
obviel.view({
    iface: 'successIface',
    render: function() {
        this.el.text("success!");
    }
});

var obvielFormsTestCase = buster.testCase('form tests', {
    setUp: function() {
        $('#jsview-area').html('<div id="viewdiv"></div>');
        $('#jsview-area').unbind();
        
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        
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
        $('#jsview-area').unview();
        $('#viewdiv').unbind();
        this.server.restore();
        obviel.view(obviel.forms.defaultErrorAreaView);
    },

// tests to implement still (and to implement in some cases):
// * absence versus presence of data
// * default values: how do we deal with them?
// * autocomplete logic
// * datepicker logic

    'basic data link sanity check': function() {
            var linkContext = {
                twoWay: true,
                name: 'foo',
                convert: function(value, source, target) {
                    return value;
                },
                convertBack: function(value, source, target) {
                    return value;
                }
            };

        var el = testel();
        var formEl = $('<form></form>');
        var inputEl = $('<input name="foo" type="text" value="" />');
        formEl.append(inputEl);
        el.append(formEl);

        var data = { foo: 'hoi' };
        inputEl.link(data, {foo: linkContext});
        formEl.link(data);
        
        $(data).setField('foo', 'dag');
        assert.equals(inputEl.val(), 'dag');
        inputEl.val('something else');
        inputEl.trigger('change');
        assert.equals(data.foo, 'something else');
        
    },

    'empty form': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                    widgets: []
            }
        });
        var formEl = $('form', el);
        assert.equals($('.form-field', formEl).length, 0);
    },

    'simple form with one field': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A textline widget'
                }]
            }
        });
        var formEl = $('form', el);
        assert(formEl.length);
        assert.equals($('.obviel-field', formEl).length, 1);
    },

    'form with one field with class': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    'class': 'foo',
                    title: 'Text',
                        description: 'A textline widget'
                }]
            }
        });
        var formEl = $('form', el);

        var fieldA_el = $('#obviel-field-test-text', formEl);
        
        assert(fieldA_el.parentView().el.hasClass('foo'));
    },

    'form with one group field with one composite field with class': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {ifaces: ['groupField'],
                     name: 'group',
                     title: 'Group',
                     widgets: [{
                         ifaces: ['compositeField'],
                         name: 'text',
                         'class': 'foo',
                         title: 'Text',
                         description: 'A composite widget',
                         widgets: [{
                             ifaces: ['textlineField'],
                             name: 'subtext',
                             title: 'SubText',
                             description: 'A textline widget'
                         }]
                     }]
                    }]
            }
        });
        var formEl = $('form', el);

        var fieldA_el = $('#obviel-field-test-group-text', formEl);
        
        assert(fieldA_el.parentView().el.hasClass('foo'));
    },


    'form with disabled field': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    disabled: true,
                    description: 'A textline widget'
                }]
            }
        });
        var formEl = $('form', el);
        assert.equals($('#obviel-field-test-text', formEl).is(':disabled'), true);
    },

    'whole form disabled': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A textline widget'
                }],
                disabled: true
            }
        });
        var formEl = $('form', el);
        assert.equals($('#obviel-field-test-text', formEl).is(':disabled'), true);
    },

    'form with two fields': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [
                    {ifaces: ['textlineField'],
                     name: 'text1',
                     title: 'Text',
                     description: 'A textline widget'
                    },
                    {ifaces: ['textlineField'],
                     name: 'text2',
                     title: 'Text',
                     description: 'A textline widget'
                    }
                ]
            }
        });
        var formEl = $('form', el);
        assert(formEl.length, 'checking for form element');
        assert.equals($('.obviel-field', formEl).length, 2);
    },

    'form with groups widgets': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets:
                [{
                    name: 'one',
                    ifaces: ['groupField'],
                    widgets: [
                        {ifaces: ['textlineField'],
                         name: 'text1',
                         title: 'Text',
                         description: 'A textline widget'
                        },
                        {ifaces: ['textlineField'],
                         name: 'text2',
                         title: 'Text',
                         description: 'A textline widget'
                        }
                    ]
                },
                 {
                     name: 'two',
                     ifaces: ['groupField'],
                     widgets: [
                         {ifaces: ['textlineField'],
                          name: 'alpha',
                          title: 'Alpha'
                         }
                     ]
                 }
                ]
            }
        });
        assert.equals($('fieldset', el).length, 2);
        assert.equals($('#obviel-fieldset-test-one', el).length, 1);
        assert.equals($('#obviel-fieldset-test-two', el).length, 1);
    },

    'form with group widget titles': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets:
                [{
                    name: 'one',
                    title: "One",
                    ifaces: ['groupField'],
                    widgets: [
                        {ifaces: ['textlineField'],
                         name: 'text1',
                         title: 'Text',
                         description: 'A textline widget'
                        },
                        {ifaces: ['textlineField'],
                         name: 'text2',
                         title: 'Text',
                         description: 'A textline widget'
                        }
                    ]
                },
                     {
                         name: 'two',
                         title: "Two",
                         ifaces: ['groupField'],
                         widgets: [
                             {ifaces: ['textlineField'],
                              name: 'alpha',
                              title: 'Alpha'
                             }
                         ]
                     }
                ]
            }
        });
        assert.equals($('#obviel-fieldset-test-one>legend', el).text(), 'One');
        assert.equals($('#obviel-fieldset-test-two>legend', el).text(), 'Two');
    },

    'form with controls': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [{
                        ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A textline widget'
                }],
                controls: [{
                    name: 'foo',
                    'class': 'fooClass',
                    action: 'something'
                }]
            }
        });
        var formEl = $('form', el);
        assert.equals($('button', el).length, 1);
        assert.equals($('button', el).attr('name'), 'foo');
        assert.equals($('button', el).attr('class'), 'obviel-control btn fooClass');
    },

    'form with non-validating control': function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                    name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A'
                }],
                controls: [{
                    name: 'foo',
                    noValidation: true
                }]
            },
            errors: errors
        });
        var formEl = $('form', el);

        var fieldA_el = $('#obviel-field-test-a', formEl);

        fieldA_el.val('not an int');
        
        var buttonEl = $('button', el);
        buttonEl.trigger('click');

        // shouldn't have done any validation
        assert.equals(errors['a'], undefined);
        },


    'form with non-validating control should still do action': function(done) {
        var el = testel();
        var errors = {};
        var controlInfo = {
            name: 'foo',
            noValidation: true,
            action: 'testUrl'
        };
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                        ifaces: ['integerField'],
                    name: 'a',
                    title: 'A'
                }],
                controls: [controlInfo]
            },
            errors: errors
        });
        var requestBody;
        this.mockJson('testUrl', function(request) {
            requestBody = request.requestBody;
            return {'ifaces': ['successIface']};
        });
        
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        // not a valid value, but it doesn't matter as we don't
        // submit any actual data with a noValidation control
        fieldEl.val('foo');

        var view = el.view();
        var buttonEl = $('button', el);
        // XXX this shows the weaknesses in the control submit API
        view.submitControl(buttonEl, controlInfo).done(function() {
            assert.equals(requestBody, null);
            // the successIface should be rendered
            assert.equals(el.text(), 'success!');
            done();
        });
    },

    'text rendering': function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [{
                    ifaces: ['textField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget'
                }]
            }
        });
        var formEl = $('form', el);
        assert.equals($('textarea', formEl).length, 1);
    },

    "boolean rendering": function() {
        var el = testel();
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [{
                    ifaces: ['booleanField'],
                        name: 'boolean',
                    title: 'Boolean',
                    description: 'A boolean widget'
                }]
            }
        });
        var formEl = $('form', el);
        assert.equals($('input[type="checkbox"]', formEl).length, 1);
    },

    // note that in these conversion and validation tests the widget is
    // created with an 'obj' attribute directly. in practice the view
    // system will actually set these for you when you render the view
    'textline convert': function() {
        var widget = new obviel.forms.TextLineWidget().clone({
            obj: {}
        });
        
        assert.equals(widget.convert('foo'), {value: 'foo'});
        assert.equals(widget.convert(''), {value: null});
    },

    'textline validate required': function() {
            var widget = new obviel.forms.TextLineWidget().clone({
                obj: {
                    validate: {
                        required: true
                    }
                }
            });
        assert.equals(widget.validate('foo'), undefined);
        assert.equals(widget.validate(null), "this field is required");
    },

    "textline validate not required": function() {
        var widget = new obviel.forms.TextLineWidget().clone({
            obj: {}
        });
        
        assert.equals(widget.validate('foo'), undefined);
        assert.equals(widget.validate(null), undefined);
    },

    "textline validate minLength": function() {
        var widget = new obviel.forms.TextLineWidget().clone({
            obj:  {
                validate: {
                    minLength: 3
                }
            }
        });
        assert.equals(widget.validate('foo'), undefined);
        assert.equals(widget.validate('fo'), "value too short");
    },

    "textline validate maxLength": function() {
        var widget = new obviel.forms.TextLineWidget().clone({
            obj: {
                validate: {
                    maxLength: 3
                }
            }
        });
        assert.equals(widget.validate('foo'), undefined);
        assert.equals(widget.validate('fooo'), "value too long");
    },

    "textline validate regular expression": function() {
        var widget = new obviel.forms.TextLineWidget().clone({
            obj: {
                validate: {
                    regs: [{
                        reg:  '^a*$',
                        message: "Should all be letter a"
                    }]
                }
            }
        });
        assert.equals(widget.validate('aaa'), undefined);
        assert.equals(widget.validate('bbb'), "Should all be letter a");
    },

    // this would duplicate the textline tests, so just do a few for sampling
        "text convert": function() {
            var widget = new obviel.forms.TextWidget().clone({
                obj: { }
            });
            
            assert.equals(widget.convert('foo'), {value: 'foo'});
            assert.equals(widget.convert(''), {value: null});
        },

    "text validate regular expression": function() {
        var widget = new obviel.forms.TextWidget().clone({
            obj: {
                validate: {
                    regs: [{
                        reg:  '^a*$',
                        message: "Should all be letter a"
                    }]
                }
            }
        });
        assert.equals(widget.validate('aaa'), undefined);
        assert.equals(widget.validate('bbb'), "Should all be letter a");
    },

    "integer convert not an integer": function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {}
        });
        
        assert.equals(widget.convert('foo'), {'error': 'not a number'});
    },

    "integer convert not an integer but float": function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {}
        });
        assert.equals(widget.convert('1.5'), {'error': 'not an integer number'});
    },

    "integer convert but empty": function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {}
        });
        assert.equals(widget.convert(''), {value: null});
    },

    'integer validate required': function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {
                validate: {
                    required: true
                }
            }
        });
        assert.equals(widget.validate(1), undefined);
        assert.equals(widget.validate(null), 'this field is required');
    },

    'integer validate not required': function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {
                validate: {
                    required: false
                }
            }
        });
        assert.equals(widget.validate(1), undefined);
        assert.equals(widget.validate(null), undefined);
    },

    'integer validate negative': function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {
                validate: {
                }
            }
        });
        assert.equals(widget.validate(-1), 'negative numbers are not allowed');
    },

    'integer validate allow negative': function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj: {
                validate: {
                    allowNegative: true
                }
            }
        });
        assert.equals(widget.validate(-1), undefined);
    },

    'integer validate lengths in digits': function() {
        var widget = new obviel.forms.IntegerWidget().clone({
            obj:  {
                validate: {
                    length: 3,
                    allowNegative: true
                }
            }
        });
        assert.equals(widget.validate(111), undefined);
        assert.equals(widget.validate(1111), 'value must be 3 digits long');
        assert.equals(widget.validate(11), 'value must be 3 digits long');
        assert.equals(widget.validate(-111), undefined);
        assert.equals(widget.validate(-1111), 'value must be 3 digits long');
        assert.equals(widget.validate(-11), 'value must be 3 digits long');
    },

    'float convert': function() {
        var widget = new obviel.forms.FloatWidget().clone({
            obj: {}
        });
        
        assert.equals(widget.convert('1.2'), {value: 1.2});
        assert.equals(widget.convert('1'), {value: 1});
        assert.equals(widget.convert('-1.2'), {value: -1.2});
        assert.equals(widget.convert('.2'), {value: 0.2});
        assert.equals(widget.convert('-1'), {value: -1});
        assert.equals(widget.convert('-1.2'), {value: -1.2});
        assert.equals(widget.convert('-.2'), {value: -0.2});
        assert.equals(widget.convert(''), {value: null});
        assert.equals(widget.convert('foo'), {error: 'not a float'});
        assert.equals(widget.convert('1.2.3'), {error: 'not a float'});
        assert.equals(widget.convert('1,2'), {error: 'not a float'});
        assert.equals(widget.convert('-'), {error: 'not a float'});
        assert.equals(widget.convert('.'), {error: 'not a float'});
    },

    'float convert different separator': function() {
        var widget = new obviel.forms.FloatWidget().clone({
            obj:  {
                validate: {
                    separator: ','
                }
            }
        });
        assert.equals(widget.convert('1,2'), {value: 1.2});
        assert.equals(widget.convert('1'), {value: 1});
        assert.equals(widget.convert('-1,2'), {value: -1.2});
        assert.equals(widget.convert(''), {value: null});
        assert.equals(widget.convert('foo'), {error: 'not a float'});
        assert.equals(widget.convert('1.2'), {error: 'not a float'});
    },

    'float validate required': function() {
        var widget = new obviel.forms.FloatWidget().clone({
            obj: {
                validate: {
                    required: true
                }
            }
        });
        assert.equals(widget.validate(null), 'this field is required');


        widget = new obviel.forms.FloatWidget().clone({
            obj: {
                validate: {
                    required: false
                }
            }
        });
        
        assert.equals(widget.validate(null), undefined);
    },

    'float validate negative': function() {
        var widget = new obviel.forms.FloatWidget().clone({
            obj: {
                validate: {
                }
            }
        });
        assert.equals(widget.validate(-1.2), 'negative numbers are not allowed');
    },

    'decimal convert': function() {
        var widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                }
            }
        });
        assert.equals(widget.convert('1.2'), {value: '1.2'});
        assert.equals(widget.convert('1'), {value: '1'});
        assert.equals(widget.convert('.2'), {value: '.2'});
        assert.equals(widget.convert('-1'), {value: '-1'});
        assert.equals(widget.convert('-1.2'), {value: '-1.2'});
        assert.equals(widget.convert('-.2'), {value: '-.2'});
        assert.equals(widget.convert(''), {value: null});
        assert.equals(widget.convert('1.2.3'), {error: 'not a decimal'});
        assert.equals(widget.convert('.'), {error: 'not a decimal'});
        assert.equals(widget.convert('foo'), {error: 'not a decimal'});
        assert.equals(widget.convert('-'), {error: 'not a decimal'});
    },

    'decimal convert different separator': function() {
        var widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                    separator: ','
                }
            }
        });
        assert.equals(widget.convert('1,2'), {value: '1.2'});
        assert.equals(widget.convert('1'), {value: '1'});
        assert.equals(widget.convert('-1,2'), {value: '-1.2'});
        assert.equals(widget.convert(''), {value: null});
        assert.equals(widget.convert('foo'), {error: 'not a decimal'});
        assert.equals(widget.convert('1.2'), {error: 'not a decimal'});
    },

    'decimal validate': function() {
        var widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                }
            }
        });

        assert.equals(widget.validate('1.2'), undefined);
        assert.equals(widget.validate('-1.2'), 'negative numbers are not allowed');

        widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                    allowNegative: true
                }
            }
        });
        
        assert.equals(widget.validate('-1.2'), undefined);

        widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                    allowNegative: true,
                    minBeforeSep: 2,
                    maxBeforeSep: 5,
                    minAfterSep: 2,
                    maxAfterSep: 5
                }
            }
        });
        

        assert.equals(widget.validate('1.22'),
              'decimal must contain at least 2 digits before the decimal mark');
        assert.equals(widget.validate('11.22'),
              undefined);
        assert.equals(widget.validate('11111.22'),
              undefined);
        assert.equals(widget.validate('111111.22'),
              'decimal may not contain more than 5 digits before the decimal mark');
        assert.equals(widget.validate('22.1'),
              'decimal must contain at least 2 digits after the decimal mark');
        assert.equals(widget.validate('22.11'),
              undefined);
        assert.equals(widget.validate('22.11111'),
              undefined);
        assert.equals(widget.validate('22.111111'),
              'decimal may not contain more than 5 digits after the decimal mark');

        assert.equals(widget.validate('-1.22'),
              'decimal must contain at least 2 digits before the decimal mark');
        assert.equals(widget.validate('-11.22'),
              undefined);
        assert.equals(widget.validate('-11111.22'),
              undefined);
        assert.equals(widget.validate('-111111.22'),
              'decimal may not contain more than 5 digits before the decimal mark');
        assert.equals(widget.validate('-22.1'),
              'decimal must contain at least 2 digits after the decimal mark');
        assert.equals(widget.validate('-22.11'),
              undefined);
        assert.equals(widget.validate('-22.11111'),
              undefined);
        assert.equals(widget.validate('-22.111111'),
              'decimal may not contain more than 5 digits after the decimal mark');
        
        widget = new obviel.forms.DecimalWidget().clone({
                obj: {
                    validate: {
                            allowNegative: true
                    }
                }
        });

        
        assert.equals(widget.validate('1'), undefined);
        assert.equals(widget.validate('.1'), undefined);

        widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                    required: true
                }
            }
        });
        
        assert.equals(widget.validate(null), 'this field is required');

        widget = new obviel.forms.DecimalWidget().clone({
            obj: {
                validate: {
                    required: false
                    }
            }
            });
        
        assert.equals(widget.validate(null), undefined);
    },

    "form starts out with empty data": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['textlineField'],
                        name: 'a',
                        title: 'A'
                    },
                    {
                        ifaces: ['integerField'],
                        name: 'b',
                        title: 'B'
                    },
                    {
                        ifaces: ['integerField'],
                        name: 'c',
                            title: 'C',
                        defaultvalue: 1
                    }
                    
                ]
            },
            data: data,
            errors: errors
        });

        assert(data.a === null);
        assert(data.b === null);
        assert.equals(data.c, 1);
    },

    "form disabled with data": function() {
        var el = testel();
        var data = {'a': 'hello world'};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['textlineField'],
                        name: 'a',
                        title: 'A',
                        disabled: true
                    }
                ]
            },
            data: data,
            errors: errors
        });
        assert.equals($('#obviel-field-test-a', el).val(), 'hello world');
    },


    "composite datalink": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['compositeField'],
                        name: 'composite',
                        widgets: [
                                {
                                    ifaces: ['textlineField'],
                                    name: 'a',
                                    title: 'A'
                                },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }

                        ]
                    }
                ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-composite-a', formEl);
        var fieldB_el = $('#obviel-field-test-composite-b', formEl);
        
        fieldA_el.val('foo');
        fieldB_el.val('not an int'); // not an int
        fieldA_el.trigger('change');
        fieldB_el.trigger('change');

        assert.equals(errors.composite.a, '');
        assert.equals(errors.composite.b, 'not a number');
        assert.equals(data.composite.a, 'foo');
        assert.equals(data.composite.b, null); // conversion failed so null

        // now put in the right value
        fieldB_el.val('3');
        fieldB_el.trigger('change');
        assert.equals(errors.composite.b, '');
        assert.equals(data.composite.b, 3);
    },

    "composite back datalink": function() {
            var el = testel();
        var data = {};

        el.render({
            ifaces: ['viewform'],
                form: {
                    name: 'test',
                    widgets: [
                            {
                                ifaces: ['compositeField'],
                                name: 'composite',
                                title: 'Test',
                                widgets: [
                                    {
                                        ifaces: ['textlineField'],
                                        name: 'a',
                                        title: 'A'
                                    },
                                    {
                                        ifaces: ['integerField'],
                                        name: 'b',
                                        title: 'B'
                                    }

                                ]
                            }
                    ]
                },
            data: data
        });
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-composite-a', formEl);
        var fieldB_el = $('#obviel-field-test-composite-b', formEl);
        $(data.composite).setField('a', 'Bar');
        $(data.composite).setField('b', 3);
        
        assert.equals(fieldA_el.val(), 'Bar');
        assert.equals(fieldB_el.val(), '3');
        
        $(data.composite).setField('a', null);
        assert.equals(fieldA_el.val(), '');
    },


    "composite empty": function() {
        var el = testel();
        var data = {};
            var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                    widgets: [
                        {
                                ifaces: ['compositeField'],
                            name: 'composite',
                            widgets: [
                                {
                                    ifaces: ['textlineField'],
                                    name: 'a',
                                        title: 'A'
                                },
                                {
                                    ifaces: ['integerField'],
                                    name: 'b',
                                    title: 'B'
                                }

                            ]
                        }
                    ]
            },
            data: data,
            errors: errors
        });
        assert(data.composite.a === null);
        assert(data.composite.b === null);
    },

    "nested composite datalink": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['compositeField'],
                        name: 'composite',
                        widgets: [
                            {
                                ifaces: ['compositeField'],
                                name: 'composite',
                                widgets: [
                                    {
                                        ifaces: ['textlineField'],
                                        name: 'a',
                                        title: 'A'
                                        
                                    },
                                    {
                                        ifaces: ['integerField'],
                                        name: 'b',
                                        title: 'B'
                                    }
                                    
                                ]
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }
                        ]
                    }
                ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);
        var fieldCompositeCompositeA_el = $(
            '#obviel-field-test-composite-composite-a', formEl);
        var fieldCompositeCompositeB_el = $(
            '#obviel-field-test-composite-composite-b', formEl);
        var fieldCompositeB_el = $(
            '#obviel-field-test-composite-b', formEl);
        
        fieldCompositeCompositeA_el.val('foo');
        fieldCompositeCompositeB_el.val('3');
        fieldCompositeB_el.val('4');
        
        fieldCompositeCompositeA_el.trigger('change');
        fieldCompositeCompositeB_el.trigger('change');
        fieldCompositeB_el.trigger('change');

        assert.equals(data.composite.composite.a, 'foo');
            assert.equals(data.composite.composite.b, 3);
        assert.equals(data.composite.b, 4);
    },

    "repeating entries show up": function() {
        var el = testel();
        var data = {repeating: [{a: 'foo', b: 1}, {a: 'bar', b: 2}]};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
                form: {
                    name: 'test',
                    widgets: [
                        {
                            ifaces: ['repeatingField'],
                            name: 'repeating',
                            widgets: [
                                {
                                    ifaces: ['textlineField'],
                                    name: 'a',
                                    title: 'A'
                                },
                                {
                                    ifaces: ['integerField'],
                                    name: 'b',
                                    title: 'B'
                                }

                            ]
                        }
                    ]
                },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);
        var field0_aEl = $('#obviel-field-test-repeating-0-a', formEl);
        var field0_bEl = $('#obviel-field-test-repeating-0-b', formEl);
        var field1_aEl = $('#obviel-field-test-repeating-1-a', formEl);
        var field1_bEl = $('#obviel-field-test-repeating-1-b', formEl);

        assert.equals(field0_aEl.val(), 'foo');
        assert.equals(field0_bEl.val(), '1');
        assert.equals(field1_aEl.val(), 'bar');
        assert.equals(field1_bEl.val(), '2');

    },

    "repeating datalink": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['repeatingField'],
                        name: 'repeating',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A'
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }

                        ]
                        }
                ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);

        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');

        assert.equals(data.repeating.length, 1);
        assert.equals(errors.repeating.length, 1);
        
        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);
        
        fieldA_el.val('foo');
        fieldB_el.val('not an int'); // not an int
        fieldA_el.trigger('change');
        fieldB_el.trigger('change');

        assert.equals(errors.repeating[0].a, '');
        assert.equals(errors.repeating[0].b, 'not a number');
        assert.equals(data.repeating[0].a, 'foo');
        assert.equals(data.repeating[0].b, null); // conversion failed so null

        // now put in the right value
        fieldB_el.val('3');
        fieldB_el.trigger('change');
        assert.equals(errors.repeating[0].b, '');
        assert.equals(data.repeating[0].b, 3);
    },

    "repeating defaults": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['repeatingField'],
                        name: 'repeating',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A',
                                defaultvalue: 'foo'
                            },
                            {
                                    ifaces: ['integerField'],
                                    name: 'b',
                                title: 'B',
                                defaultvalue: 1
                            }

                        ]
                    }
                ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);

        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');

        assert.equals(data.repeating.length, 1);
        assert.equals(errors.repeating.length, 1);
        
        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);

        assert.equals(fieldA_el.val(), 'foo');
        assert.equals(fieldB_el.val(), '1');

        assert.equals(data.repeating[0].a, 'foo');
        assert.equals(data.repeating[0].b, 1);
        
    },

    "repeating empty entries without defaults": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['repeatingField'],
                        name: 'repeating',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A'
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }

                        ]
                    }
                ]
            },
            data: data,
            errors: errors
            });
        
        var formEl = $('form', el);

            var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');

        assert.equals(data.repeating.length, 1);
        assert.equals(errors.repeating.length, 1);
        
        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);

        assert(data.repeating[0].a === null);
        assert(data.repeating[0].b === null);
        
    },

    "repeating back datalink": function() {
        var el = testel();
        var data = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['repeatingField'],
                        name: 'repeating',
                        title: 'Test',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A'
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }

                        ]
                    }
                ]
            },
            data: data
        });
            var formEl = $('form', el);
        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');
            
        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);
        
        $(data.repeating[0]).setField('a', 'Bar');
        $(data.repeating[0]).setField('b', 3);
        
        assert.equals(fieldA_el.val(), 'Bar');
        assert.equals(fieldB_el.val(), '3');
        
        $(data.repeating[0]).setField('a', null);
        assert.equals(fieldA_el.val(), '');
    },


    "repeating remove item": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                    widgets: [
                        {
                            ifaces: ['repeatingField'],
                            name: 'repeating',
                            widgets: [
                                {
                                    ifaces: ['textlineField'],
                                    name: 'a',
                                    title: 'A'
                                },
                                {
                                    ifaces: ['integerField'],
                                    name: 'b',
                                    title: 'B'
                                }

                            ]
                        }
                    ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);

        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');
        addButton.trigger('click');
        addButton.trigger('click');
        
        assert.equals(data.repeating.length, 3);
        assert.equals(errors.repeating.length, 3);
        
        var field0_aEl = $('#obviel-field-test-repeating-0-a', formEl);
        var field0_bEl = $('#obviel-field-test-repeating-0-b', formEl);

        var field1_aEl = $('#obviel-field-test-repeating-1-a', formEl);
        var field1_bEl = $('#obviel-field-test-repeating-1-b', formEl);
        
        var field2_aEl = $('#obviel-field-test-repeating-2-a', formEl);
        var field2_bEl = $('#obviel-field-test-repeating-2-b', formEl);
        
        
        field0_aEl.val('foo');
        field0_bEl.val('10');
        field1_aEl.val('bar');
        field1_bEl.val('20');
        field2_aEl.val('baz');
        field2_bEl.val('30');

        change(field0_aEl);
        change(field0_bEl);
        change(field1_aEl);
        change(field1_bEl);
        change(field2_aEl);
        change(field2_bEl);
        
        assert.equals(data.repeating[0].a, 'foo');
        assert.equals(data.repeating[0].b, 10);
        assert.equals(data.repeating[1].a, 'bar');
        assert.equals(data.repeating[1].b, 20);
        assert.equals(data.repeating[2].a, 'baz');
        assert.equals(data.repeating[2].b, 30);

        // now remove entry indexed 1
        var removeButton = $('.obviel-repeat-remove-button',
                             field1_aEl.parent().parent().parent().parent());
        removeButton.trigger('click');

        assert.equals(data.repeating.length, 2);
        assert.equals(errors.repeating.length, 2);

        field1_aEl = $('#obviel-field-test-repeating-1-a', formEl);
        field1_bEl = $('#obviel-field-test-repeating-1-b', formEl);
        assert.equals(field1_aEl.length, 0);
        assert.equals(field1_bEl.length, 0);
        
        assert.equals(data.repeating[0].a, 'foo');
        assert.equals(data.repeating[0].b, 10);
        assert.equals(data.repeating[1].a, 'baz');
        assert.equals(data.repeating[1].b, 30);

        // do some modifications, should end up in the right place
        field0_aEl.val('qux');
        field0_bEl.val('11');
        field2_aEl.val('hoi');
        field2_bEl.val('44');

        change(field0_aEl);
        change(field0_bEl);
        change(field2_aEl);
        change(field2_bEl);

        assert.equals(data.repeating[0].a, 'qux');
        assert.equals(data.repeating[0].b, 11);
        assert.equals(data.repeating[1].a, 'hoi');
        assert.equals(data.repeating[1].b, 44);

        // now add a field again, new entry should show up with higher number
        // than seen before, to avoid overlap
        addButton.trigger('click');
        var field3_aEl = $('#obviel-field-test-repeating-3-a', formEl);
        var field3_bEl = $('#obviel-field-test-repeating-3-b', formEl);
        assert.equals(field3_aEl.length, 1);
        assert.equals(field3_bEl.length, 1);
        assert.equals(data.repeating.length, 3);
    },

    "repeating removing added item from data": function() {
        var el = testel();
        var data = {repeating: [
            {a: 'foo', b: 10},
            {a: 'bar', b: 20},
                {a: 'baz', b: 30}
            ]};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['repeatingField'],
                        name: 'repeating',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A'
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }

                        ]
                    }
                ]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);
        
        assert.equals(data.repeating.length, 3);
        assert.equals(errors.repeating.length, 3);
        
        var field0_aEl = $('#obviel-field-test-repeating-0-a', formEl);
        var field0_bEl = $('#obviel-field-test-repeating-0-b', formEl);

        var field1_aEl = $('#obviel-field-test-repeating-1-a', formEl);
        var field1_bEl = $('#obviel-field-test-repeating-1-b', formEl);
        
        var field2_aEl = $('#obviel-field-test-repeating-2-a', formEl);
        var field2_bEl = $('#obviel-field-test-repeating-2-b', formEl);
        
        field0_aEl.val('foo-changed');
        field0_bEl.val('11');
        field1_aEl.val('bar-changed');
        field1_bEl.val('21');
        field2_aEl.val('baz-changed');
        field2_bEl.val('31');

        change(field0_aEl);
        change(field0_bEl);
        change(field1_aEl);
        change(field1_bEl);
        change(field2_aEl);
        change(field2_bEl);
        
        assert.equals(data.repeating[0].a, 'foo-changed');
        assert.equals(data.repeating[0].b, 11);
            assert.equals(data.repeating[1].a, 'bar-changed');
        assert.equals(data.repeating[1].b, 21);
        assert.equals(data.repeating[2].a, 'baz-changed');
        assert.equals(data.repeating[2].b, 31);

        // now remove entry indexed 1
        var removeButton = $('.obviel-repeat-remove-button',
                             field1_aEl.parent().parent().parent().parent());
        removeButton.trigger('click');

        assert.equals(data.repeating.length, 2);
        assert.equals(errors.repeating.length, 2);

        field1_aEl = $('#obviel-field-test-repeating-1-a', formEl);
        field1_bEl = $('#obviel-field-test-repeating-1-b', formEl);
        assert.equals(field1_aEl.length, 0);
        assert.equals(field1_bEl.length, 0);
        
        assert.equals(data.repeating[0].a, 'foo-changed');
        assert.equals(data.repeating[0].b, 11);
        assert.equals(data.repeating[1].a, 'baz-changed');
        assert.equals(data.repeating[1].b, 31);

        // do some modifications, should end up in the right place
        field0_aEl.val('qux');
        field0_bEl.val('12');
        field2_aEl.val('hoi');
        field2_bEl.val('42');

        change(field0_aEl);
        change(field0_bEl);
        change(field2_aEl);
        change(field2_bEl);

        assert.equals(data.repeating[0].a, 'qux');
        assert.equals(data.repeating[0].b, 12);
        assert.equals(data.repeating[1].a, 'hoi');
        assert.equals(data.repeating[1].b, 42);

        // now add a field again, new entry should show up with higher number
        // than seen before, to avoid overlap
        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');
        var field3_aEl = $('#obviel-field-test-repeating-3-a', formEl);
        var field3_bEl = $('#obviel-field-test-repeating-3-b', formEl);
        assert.equals(field3_aEl.length, 1);
        assert.equals(field3_bEl.length, 1);
        assert.equals(data.repeating.length, 3);
    },


    "textline datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                        validate: {
                        }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
            var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('foo');
        fieldEl.trigger('change');
        assert.equals(data.a, 'foo');
    },

    "textline back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        $(data).setField('a', 'Bar');
        assert.equals(fieldEl.val(), 'Bar');
        $(data).setField('a', null);
        assert.equals(fieldEl.val(), '');
    },

    "integer datalink conversion error": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data,
            
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('foo'); // not an int
        fieldEl.trigger('change');
        assert.equals(errors.a, 'not a number');
        assert.equals(fieldEl.parentView().error(), 'not a number');
        assert.equals(data.a, null);
    },

    "integer datalink without error": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('3');
        fieldEl.trigger('change');
        assert.equals(data.a, 3);
    },


    "integer back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                    name: 'test',
                    widgets: [{
                        ifaces: ['integerField'],
                        name: 'a',
                        title: 'A',
                        description: 'A',
                        validate: {
                        }
                    }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        $(data).setField('a', 1);
        assert.equals(fieldEl.val(), 1);
    },

    "float datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['floatField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('3.3');
        fieldEl.trigger('change');
        assert.equals(data.a, 3.3);
    },

    "float back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                        ifaces: ['floatField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
                },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', 3.4);
        assert.equals(fieldEl.val(), '3.4');
    },

    "float back datalink different sep": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['floatField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                        separator: ','
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', 3.4);
        assert.equals(fieldEl.val(), '3,4');
    },

    "decimal datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['decimalField'],
                        name: 'a',
                        title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('3.3');
        fieldEl.trigger('change');
        assert.equals(data.a, '3.3');
    },

    "decimal back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['decimalField'],
                        name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', '3.4');
        assert.equals(fieldEl.val(), '3.4');
    },

    "decimal back datalink different sep": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['decimalField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                        separator: ','
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', '3.4');
            assert.equals(fieldEl.val(), '3,4');
    },

    "boolean datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['booleanField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        // starts as off
        fieldEl.trigger('change');
        assert.equals(data.a, false);
        
        // set to on
        fieldEl.prop('checked', true);
        fieldEl.trigger('change');
        assert.equals(data.a, true);

        // turn off again
        fieldEl.prop('checked', false);
        fieldEl.trigger('change');
        assert.equals(data.a, false);
    },

    "boolean back datalink": function() {
        var el = testel();
            var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                    widgets: [{
                        ifaces: ['booleanField'],
                        name: 'a',
                        title: 'A',
                        description: 'A',
                        validate: {
                        }
                    }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', true);
        assert.equals(fieldEl.is(':checked'), true);
        
        $(data).setField('a', false);
        assert.equals(fieldEl.is(':checked'), false);
    },

    "choice datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        
            fieldEl.val('foo');
        fieldEl.trigger('change');
        assert.equals(data.a, 'foo');
    },

    "choice datalink empty": function() {
        var el = testel();
        var data = {};
        el.render({
                ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        assert.equals(fieldEl.length, 1);
        fieldEl.val('');
        fieldEl.trigger('change');
        assert.equals(data.a, null);
    },

    "choice back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                        name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', 'bar');
        assert.equals(fieldEl.val(), 'bar');
    },


    "choice back datalink empty": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                    name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        $(data).setField('a', null);
        assert.equals(fieldEl.val(), '');
    },

    "choice empty": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    emptyOption: 'Empty',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        assert.equals($('option', fieldEl).length, 3);
    },

    'choice required no empty': function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                        required: true
                    }
                }]
            },
            data: data
        });

        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        assert.equals($('option', fieldEl).length, 2);
    },

    "choice no empty": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'foo', label: 'Foo'},
                              {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        assert.equals($('option', fieldEl).length, 3);
    },

    "choice no empty but own empty": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [
                        {value: '', label: 'Missing'},
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}],
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        assert.equals($('option', fieldEl).length, 3);
    },

    'choice global validation': function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};

        this.server.respondWith('POST', 'validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.a === 'wrong') {
                request.respond(200, {'Content-Type': 'application/json'},
                                JSON.stringify({'a': 'must not be wrong'}));
            } else {
                request.respond(200, {'Content-Type': 'application/json'},
                                JSON.stringify({}));
            }
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['choiceField'],
                    name: 'a',
                    title: 'A',
                    choices: [{value: 'wrong', label: 'Wrong'},
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

        this.server.autoRespond = false;
        
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        
        fieldA_el.val('wrong');

        
        // submitting this should trigger a global error
        var view = el.view();
        view.submit({});
        this.server.respond();

        assert.equals(globalErrors.a, 'must not be wrong');
            
        // it also shows up in the element
        var fieldGlobalA = $('#obviel-global-error-test-a', formEl);
        assert.equals(fieldGlobalA.text(), 'must not be wrong');
        
        // make the global validation problem go away again
        fieldA_el.val('right');
        view.submit({});
        this.server.respond();
        assert.equals(globalErrors.a, '');
        assert.equals(fieldGlobalA.text(), '');
        
    },

    "field error rendering": function() {
            var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                            minLength: 3
                    }
                }],
                    controls: [{
                        'label': 'Submit!',
                        'action': 'http://localhost'
                    }]
            },
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
        // put in a value that's too short, so should trigger error
        fieldEl.val('fo');
        fieldEl.trigger('change');
        // we now expect the error
        var errorEl = $('.obviel-field-error', formEl);
        assert.equals(errorEl.text(), 'value too short');
        // it's also in the errors object
        assert.equals(errors.text, 'value too short');
        // and the form displays that there's an error
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '1 field did not validate');
        // the submit buttons are disabled
        var controlEls = $('button.obviel-control', el);
        assert.equals(controlEls.is(':disabled'), true);
    },

    "noValidation control should not be disabled": function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                        minLength: 3
                        }
                    }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }, {
                    'label': 'noValidation',
                    noValidation: true
                }]
            },
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
        // put in a value that's too short, so should trigger error
        fieldEl.val('fo');
        fieldEl.trigger('change');
        // we now expect the error
        // the form displays that there's an error
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '1 field did not validate');
        // the validating button is disabled
        var submitEl = $("button:contains('Submit!')", el);
        assert.equals(submitEl.is(':disabled'), true);
        // the non validating button is not, however
        var noValidatingEl = $("button:contains('noValidation')", el);
        assert.equals(noValidatingEl.is(':disabled'), false);
    },

    "field error clearing": function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                        minLength: 3
                    }
                }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                    }]
            },
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
        // put in a value that's too short, so should trigger error
        fieldEl.val('fo');
        fieldEl.trigger('change');
        // we now expect the error
        var errorEl = $('.obviel-field-error', formEl);
        assert.equals(errorEl.text(), 'value too short');
        // it's also in the errors object
        assert.equals(errors.text, 'value too short');
        // there's a form error
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '1 field did not validate');
        
        // now we put in a correct value
        fieldEl.val('long enough');
        fieldEl.trigger('change');
        // we now expect the error to be gone
        assert.equals(errorEl.text(), '');
        // the errors object should also be cleared
        assert.equals(errors.text, '');
        // we don't see a form error anymore
        assert.equals(formErrorEl.text(), '');
        // the submit button isn't disabled
        var controlEls = $('button.obviel-control', el);
        assert.equals(controlEls.is(':disabled'), false);
        
    },

    "field error not seen until submit": function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                        minLength: 3
                    }
                }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
        // put in a value that's too short, so should trigger error
        fieldEl.val('fo');
        // there is no error yet
        var errorEl = $('.obviel-field-error', formEl);
        assert.equals(errorEl.text(), '');
        // don't trigger event but try submitting immediately
        var buttonEl = $('button', el);
        buttonEl.trigger('click');
        // we now expect the error
        assert.equals(errorEl.text(), 'value too short');
        // it's also in the errors object
        assert.equals(errors.text, 'value too short');
        // and there's a form error
            var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '1 field did not validate');
    },

    "composite field error not seen until submit": function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['compositeField'],
                    name: 'composite',
                    title: 'Composite',
                    widgets: [
                        {
                            ifaces: ['textlineField'],
                            name: 'a',
                            title: 'A',
                            validate: {
                                minLength: 3
                            }
                        },
                        {
                            ifaces: ['integerField'],
                            name: 'b',
                            title: 'B'
                        }
                    ]
                }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            errors: errors
        });
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-composite-a', formEl);
        var fieldB_el = $('#obviel-field-test-composite-b', formEl);
        // put in a value that's too short, so should trigger error
        fieldA_el.val('fo');
        // put in a non integer
        fieldB_el.val('not integer');
        // there is no error yet
        var errorA_el = $('#obviel-field-error-test-composite-a', formEl);
        var errorB_el = $('#obviel-field-error-test-composite-b', formEl);
        assert.equals(errorA_el.text(), '');
        assert.equals(errorB_el.text(), '');
        // don't trigger event but try submitting immediately
        var buttonEl = $('button', el);
        buttonEl.trigger('click');
        // we now expect the error
        assert.equals(errorA_el.text(), 'value too short');
        assert.equals(errorB_el.text(), 'not a number');
        // it's also in the errors object
        assert.equals(errors.composite.a, 'value too short');
        assert.equals(errors.composite.b, 'not a number');
        // and there's a form error
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '2 fields did not validate');
    },

    "repeating field error not seen until submit": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['repeatingField'],
                    name: 'repeating',
                    title: 'Repeating',
                    widgets: [
                        {
                            ifaces: ['textlineField'],
                            name: 'a',
                            title: 'A',
                            validate: {
                                minLength: 3
                            }
                        },
                        {
                            ifaces: ['integerField'],
                            name: 'b',
                            title: 'B'
                        }
                    ]
                }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            data: data,
            errors: errors
        });
        
        var formEl = $('form', el);
        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');

        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);
        // put in a value that's too short, so should trigger error
        fieldA_el.val('fo');
        // put in a non integer
        fieldB_el.val('not integer');
        // there is no error yet
        var errorA_el = $('#obviel-field-error-test-repeating-0-a', formEl);
        var errorB_el = $('#obviel-field-error-test-repeating-0-b', formEl);
        assert.equals(errorA_el.text(), '');
        assert.equals(errorB_el.text(), '');
        // don't trigger event but try submitting immediately
        var buttonEl = $('button.obviel-control', el);
        buttonEl.trigger('click');
        // we now expect the error
        assert.equals(errorA_el.text(), 'value too short');
        assert.equals(errorB_el.text(), 'not a number');
        // it's also in the errors object
        assert.equals(errors.repeating[0].a, 'value too short');
        assert.equals(errors.repeating[0].b, 'not a number');
        // and there's a form error
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '2 fields did not validate');
    },



    "actual submit": function(done) {
        var el = testel();
        var errors = {};
        var controlInfo = {
            'label': 'Submit!',
            'action': 'testUrl'
        };
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                        minLength: 3
                    }
                }],
                controls: [controlInfo]
            },
            errors: errors
        });

        var requestBody;
        this.mockJson('testUrl', function(request) {
            requestBody = $.parseJSON(request.requestBody);
            return {ifaces: ['successIface']};
        });
        
        
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
            fieldEl.val('foo');

        var buttonEl = $('button', el);
        var view = el.view();
        view.submitControl(buttonEl, controlInfo).done(function() {
            assert.equals(requestBody, {"text":"foo"});
            // the successIface should be rendered
            assert.equals(el.text(), 'success!');
            done();
        });
        
    },

    "actual submit with disabled field": function() {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
                form: {
                    name: 'test',
                    widgets: [{
                        ifaces: ['textlineField'],
                        name: 'text',
                        title: 'Text',
                        description: 'A text widget',
                        validate: {
                            minLength: 3
                        }
                    },
                              {
                                      ifaces: ['textlineField'],
                                  name: 'text2',
                                  title: 'Text2',
                                  disabled: true
                              }
                             ],
                    controls: [{
                        'label': 'Submit!',
                        'action': 'testUrl'
                    }]
                },
            errors: errors
        });

        var requestBody;
        
        this.mockJson('testUrl', function(request) {
            requestBody = $.parseJSON(request.requestBody);
            return {ifaces: ['successIface']};
        });

        this.server.autoRespond = false;
        
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-text', formEl);
        fieldEl.val('foo');
        var field2El = $('#obviel-field-test-text2', formEl);
        field2El.val('bar');
        
        var buttonEl = $('button', el);
        buttonEl.trigger('click');
        this.server.respond();
        
        assert.equals(requestBody, {"text":"foo","text2":"bar"});

        // the successIface should be rendered
        assert.equals(el.text(), 'success!');
    },

    "actual submit with composite field": function () {
        var el = testel();
        var errors = {};
        el.render({
            ifaces: ['viewform'],
                form: {
                    name: 'test',
                    widgets: [{
                        ifaces: ['compositeField'],
                        name: 'composite',
                        title: 'Composite',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A',
                                validate: {
                                        minLength: 3
                                }
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B'
                            }
                        ]
                    }],
                    controls: [{
                        'label': 'Submit!',
                        'action': 'testUrl'
                    }]
                },
            errors: errors
        });

        var requestBody;

        this.mockJson('testUrl', function(request) {
            requestBody = $.parseJSON(request.requestBody);
            return {ifaces: ['successIface']};
        });

        this.server.autoRespond = false;
        
        var formEl = $('form', el);

        var buttonEl = $('button', el);
        buttonEl.trigger('click');
        this.server.respond();
        assert.equals(requestBody, {"composite":{"a":null,"b":null}});
        // the successIface should be rendered
        assert.equals(el.text(), 'success!');

    },

    "control without action": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'text',
                    title: 'Text',
                    description: 'A text widget',
                    validate: {
                        minLength: 3
                    }
                }],
                controls: [{
                    'label': 'Do something!',
                    'class': 'doSomething'
                }]
            },
            data: data,
            errors: errors
        });



        var called = 0;
        this.server.respondWith(function() {
            called++;
        });
        this.server.autoRespond = false;
        
        var formEl = $('form', el);

        var buttonEl = $('button', el);
        buttonEl.trigger('click');
        this.server.respond();
        
        
        assert.equals(called, 0);
    },

    "existing values": function() {
        var el = testel();
        var data = {a: 'Something already',
                    b: 3};
            el.render({
                ifaces: ['viewform'],
                form: {
                    name: 'test',
                    widgets: [{
                        ifaces: ['textlineField'],
                        name: 'a',
                        title: 'A'
                    },
                              {
                                  ifaces: ['integerField'],
                                  name: 'b',
                                  title: 'B'
                              }
                             ],
                    controls: [{
                        'label': 'Submit!',
                        'action': 'http://localhost'
                    }]
                },
                data: data
            });
        var aEl = $('#obviel-field-test-a', el);
        assert.equals(aEl.val(), 'Something already');
        var bEl = $('#obviel-field-test-b', el);
        assert.equals(bEl.val(), '3');
    },

    "default values": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'a',
                    title: 'A',
                    defaultvalue: 'A default'
                },
                          {
                              ifaces: ['integerField'],
                              name: 'b',
                              title: 'B',
                              defaultvalue: 3
                          }
                             ],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                    }]
            },
            data: data
            });
        assert.equals(data.a, 'A default');
        assert.equals(data.b, 3);
        var aEl = $('#obviel-field-test-a', el);
        assert.equals(aEl.val(), 'A default');
        var bEl = $('#obviel-field-test-b', el);
        assert.equals(bEl.val(), '3');
    },

    "default values with composite": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                    {
                        ifaces: ['compositeField'],
                        name: 'composite',
                        widgets: [
                            {
                                ifaces: ['textlineField'],
                                name: 'a',
                                title: 'A',
                                defaultvalue: 'A default'
                            },
                            {
                                ifaces: ['integerField'],
                                name: 'b',
                                title: 'B',
                                defaultvalue: 3
                            }
                        ]
                    }
                ],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            data: data
        });
        assert.equals(data.composite.a, 'A default');
        assert.equals(data.composite.b, 3);
        var aEl = $('#obviel-field-test-composite-a', el);
        assert.equals(aEl.val(), 'A default');
        var bEl = $('#obviel-field-test-composite-b', el);
        assert.equals(bEl.val(), '3');
    },

    "default values interacting with existent": function() {
        var el = testel();
        var data = {a: 'Something already'};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['textlineField'],
                    name: 'a',
                    title: 'A',
                    defaultvalue: 'A default'
                },
                          {
                              ifaces: ['integerField'],
                              name: 'b',
                              title: 'B',
                              defaultvalue: 3
                          }
                         ],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            data: data
        });
        assert.equals(data.a, 'Something already');
        assert.equals(data.b, 3);
        var aEl = $('#obviel-field-test-a', el);
        assert.equals(aEl.val(), 'Something already');
        var bEl = $('#obviel-field-test-b', el);
        assert.equals(bEl.val(), '3');
    },


    "default values in composite interacting with existent": function() {
        var el = testel();
        var data = {composite: {a: 'Something already'}};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['compositeField'],
                    name: 'composite',
                    widgets: [
                        {
                            ifaces: ['textlineField'],
                            name: 'a',
                            title: 'A',
                            defaultvalue: 'A default'
                        },
                        {
                            ifaces: ['integerField'],
                            name: 'b',
                            title: 'B',
                            defaultvalue: 3
                        }
                    ]
                }],
                controls: [{
                    'label': 'Submit!',
                    'action': 'http://localhost'
                }]
            },
            data: data
        });
        assert.equals(data.composite.a, 'Something already');
        assert.equals(data.composite.b, 3);
        var aEl = $('#obviel-field-test-composite-a', el);
        assert.equals(aEl.val(), 'Something already');
        var bEl = $('#obviel-field-test-composite-b', el);
        assert.equals(bEl.val(), '3');
    },


    "global errors": function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};

        
        this.mockJson('validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.a > data.b) {
                return {
                    'a': 'must be smaller than b',
                    'b': 'must be greater than a'
                };
            }
            return {};
        });

        el.render({
            ifaces: ['viewform'],
            form: {
                    name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A'
                }, {
                    ifaces: ['integerField'],
                    name: 'b',
                    title: 'B',
                    description: 'B'
                }]
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });

        this.server.autoRespond = false;
        
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        var fieldB_el = $('#obviel-field-test-b', formEl);

        fieldA_el.val('1');
        fieldB_el.val('10');

        // submitting this, everything should be fine
        var view = el.view();
        // no action defined, so submit will succeed quietly
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, undefined);
        assert.equals(globalErrors.b, undefined);
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '');
        
        fieldA_el.val('10');
        fieldB_el.val('1');
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, 'must be smaller than b');
        assert.equals(globalErrors.b, 'must be greater than a');

        // it also shows up in the element
        var fieldGlobalA = $('#obviel-global-error-test-a', formEl);
        assert.equals(fieldGlobalA.text(), 'must be smaller than b');
        assert.equals(formErrorEl.text(), '2 fields did not validate');
        assert.equals(fieldGlobalA.parent().parent().parentView().globalError(),
                      'must be smaller than b');
        
        // make the global validation problem go away again
        fieldB_el.val('100');
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, '');
        assert.equals(globalErrors.b, '');
        assert.equals(fieldGlobalA.text(), '');
        assert.equals(formErrorEl.text(), '');
    },

    'global errors revalidate upon possible correction': function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};

        this.mockJson('validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.a > data.b) {
                return {
                    'a': 'must be smaller than b',
                    'b': 'must be greater than a'
                };
            }
            return {};
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    globalValidator: true
                }, {
                    ifaces: ['integerField'],
                    name: 'b',
                    title: 'B',
                    description: 'B',
                    globalValidator: true
                }]
                },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        var fieldB_el = $('#obviel-field-test-b', formEl);

        fieldA_el.val('1');
        fieldB_el.val('10');

        var server = this.server;
        
        server.autoRespond = false;

        // submitting this, everything should be fine
        var view = el.view();
        // no action defined, so submit will succeed quietly
        view.submit({});
        server.respond();
            
        assert.equals(globalErrors.a, undefined);
        assert.equals(globalErrors.b, undefined);
        var formErrorEl = $('.obviel-formerror', el);
        assert.equals(formErrorEl.text(), '');

        // now create global validation error
        fieldA_el.val('10');
        fieldB_el.val('1');
        
        view.submit({});
        server.respond();

        assert.equals(globalErrors.a, 'must be smaller than b');
        assert.equals(globalErrors.b, 'must be greater than a');
        
        // it also shows up in the element
        var fieldGlobalA = $('#obviel-global-error-test-a', formEl);
        assert.equals(fieldGlobalA.text(), 'must be smaller than b');
        assert.equals(formErrorEl.text(), '2 fields did not validate');
        
        // possibly make the global validation problem go away (but not)
        // by modifying one of the affected fields
        fieldA_el.val('11');
        fieldA_el.parentView().change();
        server.respond();
                
        assert.equals(globalErrors.a, 'must be smaller than b');
        assert.equals(globalErrors.b, 'must be greater than a');
        
        fieldB_el.val('100');
        fieldB_el.parentView().change();
        server.respond();
        
        // this should've resubmitted for validation, so the problem should be
        // gone already
        assert.equals(globalErrors.a, '');
        assert.equals(globalErrors.b, '');
        assert.equals(fieldGlobalA.text(), '');
        assert.equals(formErrorEl.text(), '');
    },

    'global errors do not revalidate upon non-correction': function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};

        var count = 0;
        
        this.mockJson('validate', function(request) {
            count++;
            var data = $.parseJSON(request.requestBody);
            if (data.a > data.b) {
                return {
                    'a': 'must be smaller than b',
                        'b': 'must be greater than a'
                };
            }
            return {};
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    globalValidator: true
                }, {
                    ifaces: ['integerField'],
                    name: 'b',
                    title: 'B',
                    description: 'B',
                    globalValidator: true
                }, {
                    ifaces: ['integerField'],
                    name: 'c',
                    title: 'C',
                    description: 'C'
                }]
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });

        var server = this.server;
        server.autoRespond = false;
        
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        var fieldB_el = $('#obviel-field-test-b', formEl);
        var fieldC_el = $('#obviel-field-test-c', formEl);
        fieldA_el.val('1');
        fieldB_el.val('10');
        fieldC_el.val('5');
        // submitting this, everything should be fine
        var view = el.view();
        // no action defined, so submit will succeed quietly
        view.submit({});
        server.respond();
        assert.equals(count, 1);
        
        // create error
        fieldA_el.val('10');
        fieldB_el.val('1');
        view.submit({});
        server.respond();
        
        assert.equals(globalErrors.a, 'must be smaller than b');
        assert.equals(globalErrors.b, 'must be greater than a');
        assert.equals(count, 2);
        
        // possibly make the global validation problem go away (but not)
        // by modifying unrelated field
        fieldC_el.val('55');
        fieldC_el.parentView().change();
        server.respond();
        
        // we should not have done any global validation check, as this
        // field is unrelated to global validation errors
        assert.equals(count, 2);
    },

    "global errors with repeating": function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};
        
        this.mockJson('validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.repeating[0].a === 'triggerError') {
                return {
                    'repeating': [{'a': 'error'}]
                };
            }
            return {};
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [
                        {
                            ifaces: ['repeatingField'],
                            name: 'repeating',
                            widgets: [
                                {
                                    ifaces: ['textlineField'],
                                    name: 'a',
                                    title: 'A'
                                },
                                {
                                    ifaces: ['integerField'],
                                    name: 'b',
                                        title: 'B'
                                }

                            ]
                        }
                ]
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });
        var formEl = $('form', el);

        var server = this.server;
        server.autoRespond = false;
        
        var addButton = $('.obviel-repeat-add-button', formEl);
        addButton.trigger('click');
        server.respond();
        
        var fieldA_el = $('#obviel-field-test-repeating-0-a', formEl);
        var fieldB_el = $('#obviel-field-test-repeating-0-b', formEl);
        fieldA_el.val('foo');
        fieldB_el.val('10');

        // submitting this, everything should be fine
        var view = el.view();
        // no action defined, so submit will succeed quietly
        view.submit({});
        server.respond();
        
        assert.equals(globalErrors.repeating[0].a, undefined);
        assert.equals(globalErrors.repeating[0].b, undefined);
        
        fieldA_el.val('triggerError');
        fieldB_el.val('1');
        view.submit({});
        server.respond();
        
        assert.equals(globalErrors.repeating[0].a, 'error');
        assert.equals(globalErrors.repeating[0].b, undefined);
        
        // make the global validation problem go away again
        fieldA_el.val('nothing');
        view.submit({});
        server.respond();
        
        assert.equals(globalErrors.repeating[0].a, '');
        assert.equals(globalErrors.repeating[0].b, undefined);

    },
    
    'display value': function () {
        var el = testel();
        var data = {
            a: null
        };
        var errors = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['displayField'],
                    nullValue: '?',
                    name: 'a'
                }]
            },
            data: data,
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        assert.equals(fieldEl.text(), '?');

        $(data).setField('a', 'alpha');
        assert.equals(fieldEl.text(), 'alpha');
    },

    'display label': function () {
        var el = testel();
        var data = {
            a: 'alpha'
        };
        var errors = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['displayField'],
                    nullValue: '?',
                    name: 'a',
                    valueToLabel: {
                        'alpha': 'Alpha'
                    }
                }]
            },
            data: data,
            errors: errors
        });
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);

        assert.equals(fieldEl.text(), 'Alpha');
    },

    "modify error area": function() {
        // override error area rendering
        // XXX test runner for forms doesn't clean this up yet

        obviel.view({
            iface: 'obvielFormsErrorArea',
            obvt: ('<div class="obviel-error-wrapper">' +
                   '<div class="obviel-error-content">' +
                   '<div class="obviel-error-arrow"></div>' +
                   '<div data-id="{fieldErrorId}" class="obviel-field-error"></div>' +
                   '<div data-id="{globalErrorId}" class="obviel-global-error"></div>' +
                   '</div>' +
                   '</div>')
        });
        
        var el = testel();
        var data = {};
        var errors = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                    name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data,
            
            errors: errors
        });

        // check whether newly rendered data is there
        assert.equals($('.obviel-error-arrow', el).length, 1);

        // change so we get an error
        var formEl = $('form', el);
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('foo'); // not an int
        fieldEl.trigger('change');
        // now check whether error information is indeed updated
        assert.equals($('#obviel-field-error-test-a', el).text(), 'not a number');
    },

    "error events": function() {
        var el = testel();
        var data = {};
        var errors = {};

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A',
                    validate: {
                    }
                }]
            },
            data: data,
            
            errors: errors
        });

        var formEl = $('form', el);

        // bind to error event
        
        formEl.bind('field-error.obviel-forms', function(ev) {
            $(ev.target).parents('.obviel-field').addClass('foo');
        });

        
        formEl.bind('field-error-clear.obviel-forms', function(ev) {
            $(ev.target).parents('.obviel-field').removeClass('foo');
        });
        
        var fieldEl = $('#obviel-field-test-a', formEl);
        fieldEl.val('foo'); // not an int
        fieldEl.trigger('change');

        assert(fieldEl.parents('.obviel-field').hasClass('foo'));

        fieldEl.val(1); // an int
        fieldEl.trigger('change');
        
        assert(!fieldEl.parents('.obviel-field').hasClass('foo'));
    },

    "global error events": function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};
        
        this.mockJson('validate', function(request) {
            var data = $.parseJSON(request.requestBody);
            if (data.a > data.b) {
                return {
                    'a': 'must be smaller than b',
                    'b': 'must be greater than a'
                };
            }
            return {};
        });

        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['integerField'],
                    name: 'a',
                    title: 'A',
                    description: 'A'
                }, {
                    ifaces: ['integerField'],
                    name: 'b',
                    title: 'B',
                    description: 'B'
                }]
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });
        
        this.server.autoRespond = false;
            
        var formEl = $('form', el);
        var fieldA_el = $('#obviel-field-test-a', formEl);
        var fieldB_el = $('#obviel-field-test-b', formEl);

        formEl.bind('global-error.obviel-forms', function(ev) {
            $(ev.target).parents('.obviel-field').addClass('foo');
        });
        formEl.bind('global-error-clear.obviel-forms', function(ev) {
            $(ev.target).parents('.obviel-field').removeClass('foo');
        });

        // set up global error situation
        fieldA_el.val('10');
        fieldB_el.val('1');
        var view = el.view();
        view.submit({});
        this.server.respond();
        
        assert.equals(globalErrors.a, 'must be smaller than b');
        assert.equals(globalErrors.b, 'must be greater than a');

        // the event has triggered for both fields
        assert(fieldA_el.parents('.obviel-field').hasClass('foo'));
        assert(fieldB_el.parents('.obviel-field').hasClass('foo'));

        // make the global validation problem go away again
        fieldB_el.val('100');
        view.submit({});
        this.server.respond();
        
        // the clear event has triggered for both fields
        refute(fieldA_el.parents('.obviel-field').hasClass('foo'));
        refute(fieldB_el.parents('.obviel-field').hasClass('foo'));
        
    },
    'http error in validationUrl': function() {
        var el = testel();
        var data = {};
        var errors = {};
        var globalErrors = {};

        var spy = sinon.spy();
        obviel.httpErrorHook(spy);
        
        this.server.respondWith('POST', 'validate', function(request) {
            request.respond(500, {'Content-Type': 'text/html'},
                            '<div>Internal server error</div>');
        });
        
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: []
            },
            validationUrl: 'validate',
            data: data,
            errors: errors,
            globalErrors: globalErrors
        });

        this.server.autoRespond = false;
        
        var formEl = $('form', el);
        var view = el.view();
        view.submit({});
        this.server.respond();

        assert.calledOnce(spy);
        assert.equals(spy.args[0][0].status, 500);
  }

});
