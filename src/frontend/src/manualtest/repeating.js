
$(document).ready(function() {
    var data = {};

    $('.examine').click( function() {
        console.log(data);
    });
           
    $('#testform').render({
        ifaces: ['viewform'],
        data: data,
        form: {
            widgets: [
                {
                    ifaces: ['repeatingField'],
                    name: 'repeating',
                    title: 'Repeating',
                    
                    widgets: [{
                        ifaces: ['integerField'],
                        name: 'b',
                        title: 'B'
                    },{
                        ifaces: ['textlineField'],
                        name: 'c',
                        title: 'C'
                    }]
                }
            ]
        }
    });
    

});
