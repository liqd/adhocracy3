$(window).load(function() {
    var navigation = $('#main .page_wrapper > ul')
        .addClass('styleguide-navigation')
        .prepend($('<a href="#">top</a>'))
        .hide();

    var link = $('<a href="#">navigation</a>')
        .addClass('styleguide-navigation-toggle')
        .click(function(event) {
            event.preventDefault();
            navigation.toggle('fast');
        });

    link.insertBefore(navigation);
});
