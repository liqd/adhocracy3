/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import AdhHttp = require('Adhocracy/Services/Http');


// web sockets

// first draft, using a primitive global (to the factory) web socket
// handle, and an equally primitive dictionary for registering models
// interested in updates.  (i don't think this is what we actually
// want to do once the application gets more complex, but i want to
// find out how well it works anyway.  see also angularjs github wiki,
// section 'best practice'.)

var wsuri : string = 'ws://' + window.location.host + AdhHttp.jsonPrefix + '?ws=all';

export interface IService {
    subscribe: (path : string, update : (model: any) => void) => void;
    unsubscribe: (path : string, strict ?: boolean) => void;
    destroy: () => void;
}

export function factory(adhHttp : AdhHttp.IService) : IService {
    var ws = openWs(adhHttp);
    var subscriptions = {};

    function subscribeWs(path : string, update : (model: any) => void) : void {
        subscriptions[path] = update;
    }

    function unsubscribeWs(path : string, strict ?: boolean) : void {
        if (path in subscriptions)
            delete subscriptions[path];
        else if (strict)
            throw 'unsubscribe web socket listener: no subscription for ' + path + '!'
    }

    function openWs(adhHttp : AdhHttp.IService) {
        ws = new WebSocket(wsuri);

        ws.onmessage = function(event) {
            var path = event.data;
            console.log('web socket message: update on ' + path);

            if (path in subscriptions)
                adhHttp.get(path).then(subscriptions[path]);
        };

        // some console info to keep track of things happening:
        ws.onerror = function(event) {
            console.log(event);
            console.log('ws.onerror');
        };
        ws.onopen = function() {
            console.log('ws.onopen');
        };
        ws.onclose = function() {
            console.log('ws.onclose (will try to re-open)');
            ws = openWs(adhHttp);
        };

        return ws;
    }

    function closeWs() : void {
        console.log('closeWs');
        ws.close();
    }

    return {
        subscribe: subscribeWs,
        unsubscribe: unsubscribeWs,
        destroy: closeWs,
    }
}
