(function() {
    var main = function() {
        var data = {
            'da': 'foo',
            'dau': 'foo'
        };
        
        var el = $('#testform');
        
        el.render({
            ifaces: ['viewform'],
            form: {
                widgets: [
                    {
                        ifaces: ['booleanField'],
                        name: 'a',
                        title: 'A',
                        validate: {
                            required: true
                        }
                    },
                    {
                        ifaces: ['integerField'],
                        name: 'b',
                        title: 'B'
                    },
                    {
                        ifaces: ['textField'],
                        name: 'txt',
                        title: 'TXT',
                        height: 10,
                        width: 20
                    },
                    {
                        ifaces: ['choiceField'],
                        name: 'c',
                        title: 'C',
                        choices: [
                            {value: 'foo', label: 'Foo'},
                            {value: 'bar', label: 'Bar'}
                        ]
                    },
                    {
                        ifaces: ['autocompleteField'],
                        name: 'da',
                        title: 'Autocomplete',
                        data: [
                            {value: 'foo', label: 'Foo'},
                            {value: 'bar', label: 'Bar'}
                        ],
                        defaultvalue: 'foo'
                    },
                    {
                        ifaces: ['datepickerField'],
                        name: 'dp',
                        title: 'Datepicker'
                    }  
                ],
                controls: [
                    {
                        'label': 'Examine',
                        'class': 'examine'
                    },
                    {
                        'label': 'Change',
                        'class': 'change'
                    }
                    
                ]
            },
            data: data
        });
        
        $('.examine', el).click(function(ev) {
            console.log(data);
        });
        
        $('.change', el).click(function(ev) {
            $(data).setField('da', 'bar');
        });
    };
    
    $(document).ready(function() {
        obviel.i18n.load().done(function() {
            obviel.i18n.setLocale('nl_NL').done(function() { main(); });
        });
    });
    
})();

