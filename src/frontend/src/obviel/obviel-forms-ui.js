/* a few nice jquery-ui things for Obviel forms */

(function($, obviel) {
    // pretty jQuery UI buttons
    $(document).on('button-created.obviel', function(ev) {
        $(ev.target).button();
    });

    $(document).on('button-updated.obviel', function(ev) {
        $(ev.target).button('refresh');
    });

    $(document).on('render-done.obviel', function (ev) {
        $('input[type="submit"]', ev.view.el).button();
        $('input[type="button"]', ev.view.el).button();
        $('button', ev.view.el).button();
    });

})(jQuery, obviel);
