$.mockjaxSettings.dataType = 'json';

$(document).ready(function() {
    var data = {
    };

    $.mockjax({
        url: 'global_validation',
        responseText: {a: 'An error'}
    });
    
    var el = $('#testform');
    
    el.render({
        ifaces: ['viewform'],
        form: {
            widgets: [
                {
                    ifaces: ['textlineField'],
                    name: 'a',
                    title: 'A',
                    globalValidator: true
                }
            ],
            controls: [
                {
                    'label': 'Examine',
                    'class': 'examine'
                }
            ]
        },
        validationUrl: 'global_validation',
        data: data
    });
    
});