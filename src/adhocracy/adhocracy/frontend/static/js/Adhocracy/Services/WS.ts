/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import AdhConfig = require("Adhocracy/Services/Config");


// web sockets

// first draft, using a primitive global (to the factory) web socket
// handle, and an equally primitive dictionary for registering objs
// interested in updates.  (i don't think this is what we actually
// want to do once the application gets more complex, but i want to
// find out how well it works anyway.  see also angularjs github wiki,
// section 'best practice'.)

// FIXME: the upstream should be used for sending 'ADD' and 'REMOVE'
// requests to the server, so we won't get any subscriberless content.

export interface IService {
    subscribe: (path : string, update : () => void) => void;
    unsubscribe: (path : string) => void;
    destroy: () => void;
}

export function factory(adhConfig: AdhConfig.Type) : IService {
    "use strict";

    var ws = openWs();
    var subscriptions = {};

    function subscribeWs(path : string, update : (obj: Types.Content<any>) => void) : void {
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
            throw "WS: unsubscribe: no subscription for " + path + "!";
        }
    }

    function openWs() {
        ws = new WebSocket(adhConfig.wsuri);

        ws.onmessage = function(event) {
            var path = event.data;

            if (path in subscriptions) {
                subscriptions[path]();
            }
        };

        ws.onerror = function(event) {
            return;
        };

        ws.onopen = function() {
            return;
        };

        ws.onclose = function() {
            ws = openWs();
        };

        return ws;
    }

    function closeWs() : void {
        ws.close();
    }

    return {
        subscribe: subscribeWs,
        unsubscribe: unsubscribeWs,
        destroy: closeWs
    };
}
