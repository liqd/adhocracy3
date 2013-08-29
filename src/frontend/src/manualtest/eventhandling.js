(function() {
    var foo = {
        iface: 'foo'
    };

    obviel.view({
        iface: 'foo',
        obvt: '<textarea data-on="keyup|pressed">Hello</textarea>',
        pressed: function() {
            console.log("It workz!!!");
        }
    });
    
    $(document).ready(function() {
        $('#test').render(foo);
    });
    
})();

