
$(document).ready(function() {
    /* we start with an empty data object. If we
       fill in values here, they will show up in the form */
    var data = {
    };

    /* we are going to render the form in the testform el */
    var el = $('#testform');

    /* here we render a viewform. We have included the form JSON
       inline here, but of course you can produce this on the server
       as well instead */
    el.render({
        ifaces: ['viewform'],
        form: {
            widgets: [
                {
                    ifaces: ['booleanField'],
                    name: 'bool',
                    title: 'booleanField',
                    validate: {
                        required: true
                    }
                },
                {
                    ifaces: ['integerField'],
                    name: 'integer',
                    title: 'integerField'
                },
                {
                    ifaces: ['choiceField'],
                    name: 'choice',
                    title: 'choiceField',
                    choices: [
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}
                        ]
                },
                {
                    ifaces: ['autocompleteField'],
                    name: 'auto',
                    title: 'autocompleteField',
                    data: [
                        {value: 'foo', label: 'Foo'},
                        {value: 'bar', label: 'Bar'}
                    ],
                    defaultvalue: 'foo'
                },        
                {
                    ifaces: ['datepickerField'],
                    name: 'date',
                    title: 'datepickerField'
                },
                {
                    ifaces: ['repeatingField'],
                    name: 'repeating',
                    title: 'repeatingField',
                    widgets: [
                        {
                            ifaces: ['textlineField'],
                            name: 'textline',
                            title: 'textlineField'
                        },{
                            ifaces: ['textField'],
                            name: 'text',
                            title: 'textField'
                        }]
                }
            ],
            controls: [
                {
                    'label': 'Examine data',
                    'class': 'examine btn-primary'
                },
                {
                    'label': 'Change data',
                    'class': 'change'
                },
                {
                    'label': 'Cooldown button',
                    'action': 'test',
                    'cooldown': 2000
                }
            ]
        },
        data: data
    });
    
    /* this will output the data object into the output blockquote element */
    var renderData = function() {
        var replacer = function(key, value) {
            return value;
        };
        $('#output').text(JSON.stringify(data, replacer, 4));
    };

    /* show the underlying data object */
    $('.examine', el).click(function(ev) {
        renderData();
    });

    /* this will change the data object, the form will update
       immediately */
    var counter = 0;
    
    $('.change', el).click(function(ev) {
        $(data).setField('date', '2010-10-10');
        $(data).setField('integer', counter);
        counter++;
        renderData();
    });
    
});
