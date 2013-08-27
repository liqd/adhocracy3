
$(document).ready(function() {

    var el = $('#testform');

    el.render({
        ifaces: ['viewform'],
        form: {
            widgets: [
                {
                    ifaces: ['booleanField'],
                    name: 'a',
                    title: 'A'
                },
                {
                    ifaces: ['integerField'],
                    name: 'b',
                    title: 'B'
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
                    ifaces: ['repeatingField'],
                    name: 'repeating',
                    title: 'Repeating',
                    
                    widgets: [{
                        ifaces: ['integerField'],
                        name: 'aha',
                        title: 'Aha'
                    }]
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
        }
    });
});
