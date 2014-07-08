"use strict";

(function() {
    var adhocracy : any = {};

    // setup window.adhocracy and noConflict()
    var _adhocracy = (<any>window).adhocracy;
    (<any>window).adhocracy = adhocracy;

    adhocracy.noConflict = () => {
        if ((<any>window).adhocracy === adhocracy) {
            (<any>window).adhocracy = _adhocracy;
        }
        return adhocracy;
    };

    var $;
    var origin : string;

    /**
     * Load external JavaScript asynchronously.
     */
    var loadScript = (url: string, callback: () => void) => {
        var script = document.createElement("script");
        script.async = true;
        script.src = url;

        var entry = document.getElementsByTagName("script")[0];
        entry.parentNode.insertBefore(script, entry);

        script.onload = script.onreadystatechange = () => {
            var rdyState = script.readyState;
            if (!rdyState || /complete|loaded/.test(script.readyState)) {
                callback();
                script.onload = null;
                script.onreadystatechange = null;
            }
        };
    };

    /**
     * Initialize adhocracy SDK.  Must be called before using any other methods.
     *
     * @param o Origin (e.g. https://adhocracy.de/)
     */
    adhocracy.init = (o: string, callback) => {
        origin = o;
        loadScript(origin + "frontend_static/lib/jquery/jquery.js", () => {
            $ = (<any>window).jQuery.noConflict(true);
            callback(adhocracy);
        });
    };

    /**
     * Embed adhocracy.
     *
     * Any needed data is read from the marker.
     *
     * @param selector Selector for the markers that will be replaced by adhocracy.
     */
    adhocracy.embed = (selector: string) => {
        $(selector).each((i, e) => {
            // In the future, marker may have additional attributes or
            // child elements that have influence on iframe.
            var marker = $(e);
            var iframe = $("<iframe>");
            iframe.css("border", "none");
            iframe.css("width", "100%");
            iframe.attr("src", origin + "frontend_static/root.html");
            marker.append(iframe);
        });
    };
})();
