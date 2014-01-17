/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import AdhHttp = require("Adhocracy/Services/Http");


// web sockets

// first draft, using a primitive global (to the factory) web socket
// handle, and an equally primitive dictionary for registering objs
// interested in updates.  (i don't think this is what we actually
// want to do once the application gets more complex, but i want to
// find out how well it works anyway.  see also angularjs github wiki,
// section 'best practice'.)

// FIXME: the upstream should be used for sending 'ADD' and 'REMOVE'
// requests to the server, so we won't get any subscriberless content.

var wsuri : string = "ws://" + window.location.host + AdhHttp.jsonPrefix + "?ws=all";

export interface IService {
    subscribe: (path : string, update : (obj: any) => void) => void;
    unsubscribe: (path : string) => void;
    destroy: () => void;
}

export function factory(adhHttp : AdhHttp.IService) : IService {
    var ws = openWs(adhHttp);
    var subscriptions = {};

    function subscribeWs(path : string, update : (obj: Types.Content) => void) : void {
        if (path in subscriptions) {
            throw "WS: subscribe: attempt to subscribe to " + path + " twice!";
        } else {
            subscriptions[path] = update;
        }
    }

    function unsubscribeWs(path : string) : void {
        if (path in subscriptions) {
            delete subscriptions[path];
        } else {
            throw "wS: unsubscribe: no subscription for " + path + "!";
        }
    }

    function openWs(adhHttp : AdhHttp.IService) {
        ws = new WebSocket(wsuri);

        ws.onmessage = function(event) {
            var path = event.data;
            console.log("WS message: " + path);

            if (path in subscriptions) {
                adhHttp.get(path).then(subscriptions[path]);
            }
        };

        ws.onerror = function(event) {
            console.log("WS error: ", event);
        };

        ws.onopen = function() {
            return;
        };

        ws.onclose = function() {
            ws = openWs(adhHttp);
        };

        return ws;
    }

    function closeWs() : void {
        ws.close();
    }

    return {
        subscribe: subscribeWs,
        unsubscribe: unsubscribeWs,
        destroy: closeWs,
    };
}
