(function ($, JSHINT) {
    var jshint_test = function (file, options) {
        $('#qunit-userAgent').html(navigator.userAgent);
        var body = $('body');
        var default_options = {
            sub: true,
            undef: true,
            curly: true
        };
        options = $.extend({}, default_options, options);
        $.ajax({
            url: file, 
            success: function (data) {
                var result = JSHINT(data, options);
                if (result === false) {
                    var curr_attr = $('#qunit-banner', body).attr('class');
                    if (curr_attr == 'qunit-pass' || curr_attr === null) {
                        $('#qunit-banner', body).attr('class', 'qunit-fail');
                    }
                    var ol = $('#qunit-tests', body);
                    var li = $('<li class="fail"></li>');
                    ol.append(li);
    
                    li.append('<strong><span class="module-name">' + file +
                                '</span></strong>');
                    var error_ol = $('<ol></ol>');
                    li.append(error_ol);
                    $.each(JSHINT.errors, function (idx, error) {
                        if (error) {
                            error_ol.append('<li class="fail">' + 
                            ' Line ' + error.line + ': Char ' + error.character + 
                            ' - ' + error.reason + '</li>');
                        }
                    });
                } else {
                    if ($('#qunit-banner', body).attr('class') === null) {
                        $('#qunit-banner', body).attr('class', 'qunit-pass');
                    }
                    $('#qunit-tests', body).append(
                        '<li class="pass">' +
                        '<strong><span class="module-name">' + file +
                        '</span></strong>' +
                        '<ol><li class="pass">Pass</li></ol>' +
                        '</li>' 
                    );
                }
            },
        dataType: 'text',
        error: function (jqXHR, textStatus, errorThrown) {
            console.log([jqXHR, textStatus, errorThrown]);
        },
        async: false});
    };

    JSHINT.test_url = jshint_test;
})(jQuery, JSHINT);
