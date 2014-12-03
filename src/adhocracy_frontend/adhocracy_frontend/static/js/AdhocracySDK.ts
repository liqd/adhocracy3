// FIXME: internal object for testing

(function() {
    "use strict";

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
    var appUrl : string = "/embed/";
    var embedderOrigin : string;
    var messageHandlers : any = {};

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

    var getIFrameByWindow = (win: Window) => {
        var result;
        $("iframe.adhocracy-embed").each((i, iframe) => {
            if (iframe.contentWindow === win) {
                result = iframe;
                return false;
            }
        });
        return result;
    };

    /**
     * Handle a message that was sent by another window.
     */
    var handleMessage = (name: string, data, source: Window) : void => {
        switch (name) {
            case "resize":
                var iframe = $(getIFrameByWindow(source));
                if (iframe.data("autoresize")) {
                    iframe.height(data.height);
                }
                break;
            case "requestSetup":
                adhocracy.postMessage(source, "setup", {embedderOrigin: embedderOrigin});
        }
        if (messageHandlers.hasOwnProperty(name)) {
            messageHandlers[name](data, source);
        }
    };

    /**
     * Check whether an existing embedded iframe has autourl set.
     */
    var hasAutourl = () => {
        var result = false;
        $("iframe.adhocracy-embed").each((i, iframe) => {
            if (iframe.data("autourl")) {
                result = true;
            }
        });
        return result;
    };

    var getUrlFromHash = () => {
        var url = window.location.hash;
        if (url.indexOf("#!") === 0) {
            return url.substring(2);
        }
    };

    var setHashFromUrl = (url : string) => {
        if (url.indexOf(origin) === 0) {
            window.location.hash = "!" + url.substring(origin.length);
        } else {
            throw "Embedded iframe got an src outside of origin.";
        }
    };

    var addParamsToUrl = (url : string, params : {}) => {
        if ($.isEmptyObject(params)) {
            return url;
        } else {
            var splitHash = url.split("#");
            var newQueryChar = splitHash.indexOf("?") === -1 ? "?" : "&";
            return splitHash[0] + newQueryChar + $.param(params, true) + (splitHash.length > 1 ? "#" + splitHash[1] : "");
        }
    };

    /**
     * Initialize adhocracy SDK.  Must be called before using any other methods.
     *
     * @param o Origin (e.g. https://adhocracy.de)
     */
    adhocracy.init = (o: string, callback) => {
        origin = o;
        embedderOrigin = window.location.protocol + "//" + window.location.host;

        loadScript(origin + "/static/lib/jquery/dist/jquery.js", () => {
            $ = (<any>window).jQuery.noConflict(true);

            $(window).on("message", (event) => {
                // Only parse messages from embedded windows
                //
                // FIXME: We should maintain a list of embedded windows
                if (event.originalEvent.source !== window) {
                    try {
                        var message = JSON.parse(event.originalEvent.data);
                        handleMessage(message.name, message.data, event.originalEvent.source);
                    } catch (e) {
                        // Make invalid messages fail silently as it may come
                        // from another window
                    }
                }
            });

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
            var marker = $(e);
            var data = marker.data();
            var widget = data.widget;

            delete data.widget;

            var iframe = adhocracy.getIframe(widget, data);

            marker.append(iframe);
        });
    };

    adhocracy.getIframe = (widget : string, data : any) => {
        var iframe = $("<iframe>");

        iframe.css("border", "none");
        iframe.css("width", "100%");

        var autoresize = data.autoresize;
        if (typeof autoresize === "undefined") {
            autoresize = true;
        } else {
            autoresize = Boolean(autoresize);
        }
        if (!autoresize) {
            iframe.css("height", "100%");
        }
        iframe.data("autoresize", autoresize);

        var url;
        if (widget === "plain") {

            var initialUrl;
            if (data.autourl) {
                if (hasAutourl()) {
                    throw "There's already an embedded element with enabled autourl";
                }
                initialUrl = getUrlFromHash();

                adhocracy.registerMessageHandler("urlchange", (data, source) => {
                    if (getIFrameByWindow(source) === iframe[0]) {
                        setHashFromUrl(data.url);
                    }
                });
            }
            if (typeof initialUrl === "undefined") {
                initialUrl = data.initialUrl;
            }
            if (typeof initialUrl === "undefined") {
                initialUrl = "/";
            }
            url = origin + initialUrl;
        } else {
            url = origin + appUrl + widget;
        }
        delete data.autourl;
        delete data.autoresize;
        delete data.initialUrl;
        url = addParamsToUrl(url, data);
        iframe.attr("src", url);
        iframe.addClass("adhocracy-embed");

        return iframe;
    };

    /**
     * Send a message to another window.
     *
     * @param uid ID of the target window
     * @param name Message name
     * @param data Message data
     *
     * This is redundantly implemented in
     * "Adhocracy/Services/CrossWindowMessaging".  if they start
     * growing in parallel, we should factor them out into a shared
     * module.
     */
    adhocracy.postMessage = (win: Window, name: string, data: {}) => {
        var message = {
            name: name,
            data: data
        };
        var messageString = JSON.stringify(message);

        // FIXME: use fallbacks here
        win.postMessage(messageString, origin);
    };

    adhocracy.registerMessageHandler = (name : string, callback) => {
        messageHandlers[name] = callback;
    };
})();
