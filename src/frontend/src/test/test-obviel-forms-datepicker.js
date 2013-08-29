/*global obviel:false, buster:false */

var assert = buster.assert;

var testel = function() {
    return $(document.createElement('div'));
};

var datePickerTestCase = buster.testCase('datepicker tests', {
    setUp: function() {
        $('#jsview-area').html('<div id="viewdiv"></div><div id="viewdiv2"></div>');
        $('#jsview-area').unbind();
    },
    tearDown: function() {
        $('#jsview-area').unview();
        $('#viewdiv').unbind();
    },

    'datepicker convert': function() {
        var widget = new obviel.forms.DatePickerWidget().clone({
            obj: {}
        });
        
        assert.equals(widget.convert('01/02/10'), {value: '2010-01-02'});
        assert.equals(widget.convert(''), {value: null});
        assert.equals(widget.convert('77/02/10'), {error: 'invalid date'});
        assert.equals(widget.convert('sarsem'), {error: 'invalid date'});
    },

    'datepicker validate required': function() {
        var widget = new obviel.forms.DatePickerWidget().clone({
            obj: {
                validate: {
                    required: true
                }
            }
        });
        assert.equals(widget.validate('01/02/10'), undefined);
        assert.equals(widget.validate(null), "this field is required");
    },

    "datepicker datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['datepickerField'],
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
        fieldEl.val('01/02/10');
        fieldEl.trigger('change');
        assert.equals(data.a, '2010-01-02');
    },

    "datepicker back datalink": function() {
        var el = testel();
        var data = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['datepickerField'],
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
        $(data).setField('a', '2010-03-04');
        assert.equals(fieldEl.val(), '03/04/2010');
        $(data).setField('a', null);
        assert.equals(fieldEl.val(), '');
    },

    "datepicker datalink conversion error": function() {
        var el = testel();
        var data = {};
        var errors = {};
        el.render({
            ifaces: ['viewform'],
            form: {
                name: 'test',
                widgets: [{
                    ifaces: ['datepickerField'],
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
        fieldEl.val('foo'); // not a datetime
        fieldEl.trigger('change');
        assert.equals(errors.a, 'invalid date');
        assert.equals(data.a, null);
    }
});

