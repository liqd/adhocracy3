"use strict";

// FIXME: internal object for testing

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
    var appUrl : string = "/frontend_static/root.html";
    var frames : {} = {};
    var embedderID : string;
    var embedderOrigin : string;

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
     * Generate unique IDs.
     */
    var getUID = (() => {
        var nextUID : number = 0;
        return () : string => {
            var i = nextUID++;
            return i.toString();
        };
    })();

    /**
     * Get a frame's contentWindow or the embedding window based un UID.
     */
    var getWindowByUID = (uid: string) : Window => {
        if (uid === embedderID) {
            return window;
        } else {
            var frame = frames[uid];
            return frame.contentWindow;
        }
    };

    /**
     * Handle a message that was sent by another window.
     */
    var handleMessage = (name: string, data, sender: string, event) : void => {
        if (frames.hasOwnProperty(sender)) {
            var frame = frames[sender];

            if (frame.contentWindow === event.source) {
                switch (name) {
                    case "resize":
                        $(frame).height(data.height);
                        break;
                }
            }
        }
    };

    /**
     * Initialize adhocracy SDK.  Must be called before using any other methods.
     *
     * @param o Origin (e.g. https://adhocracy.de)
     */
    adhocracy.init = (o: string, callback) => {
        origin = o;
        embedderID = getUID();
        embedderOrigin = window.location.protocol + "//" + window.location.host;

        loadScript(origin + "/frontend_static/lib/jquery/jquery.js", () => {
            $ = (<any>window).jQuery.noConflict(true);

            $(window).on("message", (event) => {
                var data = JSON.parse(event.originalEvent.data);
                handleMessage(data.name, data.data, data.sender, event.originalEvent);
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
            // In the future, marker may have additional attributes or
            // child elements that have influence on iframe.
            var marker = $(e);
            var iframe = $("<iframe>");
            var uid = getUID();

            iframe.css("border", "none");
            iframe.css("width", "100%");
            iframe.attr("src", origin + appUrl);
            iframe.addClass("adhocracy-embed");
            iframe.attr("data-adhocracy-frame-id", uid);

            marker.append(iframe);
            frames[uid] = iframe[0];

            iframe.load(() => {
                // FIXME: the code inside of the iframe is not ready when this is send.
                adhocracy.postMessage(uid, "setup", {
                    uid: uid,
                    embedderOrigin: embedderOrigin,
                    embedderID: embedderID
                });
            });
        });
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
    adhocracy.postMessage = (uid: string, name: string, data: {}) => {
        var message = {
            name: name,
            data: data,
            sender: embedderID
        };
        var messageString = JSON.stringify(message);
        var win = getWindowByUID(uid);

        // FIXME: use fallbacks here
        win.postMessage(messageString, origin);
    };
})();
