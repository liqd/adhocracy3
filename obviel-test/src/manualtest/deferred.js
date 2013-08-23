
var $ = jQuery;

$(document).ready(function() {
    var d1 = $.Deferred();
    var d2 = $.Deferred();
    
    var p1 = $.when.apply(null, [d1, d2]).done(function() {
        alert("P1");
    });
    
    var p2 = $.when(d1, d2).done(function() {
        alert("P2");
    });

    // var p1 = $.when.apply([]).done(function() {
    //     alert("P empty");
    // });
    
    //d1.resolve();
    //d2.resolve();
});

