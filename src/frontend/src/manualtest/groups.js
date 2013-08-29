
$(document).ready(function() {

    var el = $('#testform');
    
    el.render({
        ifaces: ['viewform'],
        form: {
            widgets: [
                {
                    ifaces: ['groupField'],
                    name: 'alpha',
                    title: 'Alpha',
                    widgets: [
                        { ifaces: ['integerField'],
                          name: 'a',
                          title: 'A'
                        },
                        { ifaces: ['integerField'],
                          name: 'b',
                          title: 'B'
                        }
                    ]
                },
                {
                    name: 'beta',
                    title: 'Beta',
                    ifaces: ['groupField'],
                    widgets: [
                        { ifaces: ['integerField'],
                          name: 'c',
                          title: 'C'
                        },
                        { ifaces: ['integerField'],
                          name: 'd',
                          title: 'D'
                        }
                    ]
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
