
$(document).ready(function() {
    var data = {};

           
    $('#testform').render({
        ifaces: ['viewform'],
        form: {
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
                            name: 'c',
                            title: 'C'
                        }
                    ]
                }
            ]
        }
    });
           

});