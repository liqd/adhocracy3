/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>

import AdhConfig = require("../Config/Config");

var pkgLocation = "/WebSocket";

// FIXME: consider refactoring this service into several smaller
// services ("do one thing").


/**
 * The Web Sockets Service
 *
 * This module provides a callback-based API to the consumer modules
 * for keeping up to date with relevant changes on the server side.
 * The network protocol is specified in ./docs/source/websockets.rst.
 */


//////////////////////////////////////////////////////////////////////
// exported Types

export interface IService {
    /**
     * Register a callback to a resource.  If no other callbacks are
     * registered under this resource, send subscribe message to
     * server.
     *
     * This function is a rough equivalent to $.on(), but handles
     * unregistrations differently.
     */
    register : (path : string, callback : (event : IServerEvent) => void) => string;

    /**
     * Unregister a callback from a resource.  If no other callbacks
     * are registered, send unsubscribe message to server.
     *
     * Roughly equivalent to $.off() (see comment above).
     */
    unregister : (path : string, id : string) => void;
}

/**
 * this is the websocket as provided by the browser.  it has to be
 * passed to the WebSocket factory as a separate service in order to make
 * unit testing possible (see below).
 */
export interface IRawWebSocket {
    send : (msg : string) => void;
    onmessage : (event : {data : string}) => void;
    onerror : (event : any) => void;
    onopen : (event : any) => void;
    onclose : (event : any) => void;
    readyState : number;
    CONNECTING : number;
    OPEN : number;
    CLOSING : number;
    CLOSED : number;
}

/**
 * structure of the parameter called to the consumer callbacks.  (this
 * type is slightly more general than would be nice due to
 * technicalities of the adhocracy websocket protocol and the lack of
 * disjunctive types in typescript.)
 */
export interface IServerEvent {
    event? : string;
    resource? : string;
    child? : string;
    version? : string;
}


//////////////////////////////////////////////////////////////////////
// internal Types

interface Request {
    action : string;
    resource : string;
}

interface ResponseOk {
    status? : string;
    action? : string;
    resource? : string;
}

interface ResponseError {
    error? : string;
    details? : string;
}

interface ServerMessage extends ResponseOk, ResponseError, IServerEvent {};


//////////////////////////////////////////////////////////////////////
// the Subscriptions class

/**
 * A Subscriptions instance is a dictionary of dictionaries.  The first
 * maps a resource to all its subscribed callbacks; the second maps
 * callback identifiers to actual callbacks.
 */

class Subscriptions {
    constructor(private _createCallbackId : () => string) {}

    private _dict : {
        [name : string]: {
            [id : string]: (event : IServerEvent) => void
        }
    } = {};

    /**
     * Take a resource and call all subscribed callbacks.
     */
    public notify = (event : IServerEvent) : void => {
        var _self = this;

        if (_self._dict.hasOwnProperty(event.resource)) {
            var cbs = _self._dict[event.resource];
            for (var cbid in cbs) {
                if (cbs.hasOwnProperty(cbid)) {
                    cbs[cbid](event);
                }
            }
        } else {
            throw "WebSocket: got notification of event that i haven't subscribed!";
        }
    };

    /**
     * Call a given function on all callbacks.  (Needed e.g. for
     * copying pending subscriptions to active subscriptions.)
     */
    public forAll = (cmd : (resource : string, id : string, callback : (event : IServerEvent) => void) => void) : void => {
        var _self = this;
        var _dict = _self._dict;

        for (var resource in _dict) {
            if (_dict.hasOwnProperty(resource)) {
                for (var id in _dict[resource]) {
                    if (_dict[resource].hasOwnProperty(id)) {
                        cmd(resource, id, _dict[resource][id]);
                    }
                }
            }
        }
    };

    /**
     * Are there subscriptions on a resource?  (We need to know before
     * we notify the server of an (un-) subscription.)  If id is
     * given, only check if this particular id contains a callback.
     * (needed for detection of redundant calls to unregister.)
     */
    public alive = (resource : string, id? : string) : boolean => {
        var _self = this;
        var _dict = _self._dict;

        if (id === null || typeof id === "undefined") {
            return (
                _dict.hasOwnProperty(resource) &&
                    Object.keys(_dict[resource]).length > 0);
        } else {
            return (
                _dict.hasOwnProperty(resource) &&
                    _dict[resource].hasOwnProperty(id));
        }
    };

    /**
     * Callback identifiers are generated by .add during addition
     */
    public add = (
        resource : string,
        callback : (event : IServerEvent) => void,
        id? : string,
        notifyServer? : () => void
    ) : string => {
        var _self = this;
        var _dict = _self._dict;

        // if there are no other subscriptions under this resource
        // yet, notify server (if applicable).
        if (!_self.alive(resource) && typeof notifyServer === "function") {
            notifyServer();
        }

        if (id === null || typeof id === "undefined") {
            id = _self._createCallbackId();
        }

        if (!_dict.hasOwnProperty(resource)) {
            _dict[resource] = {};
        }

        if (_dict[resource].hasOwnProperty(id)) {
            throw ("WebSocket: attempt to Subscription().add under an existing path / id: " + id);
        }

        _dict[resource][id] = callback;
        return id;
    };

    /**
     * Identify a callback by resource and id, and delete it.
     */
    public del = (
        resource : string,
        id : string,
        notifyServer? : () => void
    ) : void => {
        var _self = this;
        var _dict = _self._dict;

        if (_dict.hasOwnProperty(resource)) {
            if (_dict[resource].hasOwnProperty(id)) {
                delete _dict[resource][id];
            }
            if (_dict[resource] === {}) {
                delete _dict[resource];
            }
        }

        // if there are no other subscriptions under this resource
        // left, notify server (if applicable).
        if (!_self.alive(resource) && typeof notifyServer === "function") {
            notifyServer();
        }
    };
}


//////////////////////////////////////////////////////////////////////
// factory functions

/**
 * The WebSocket factory takes a config service and a IRawWebSocket
 * generator service.  Consumers of this service should call the
 * factory function that only takes a config service, and creates the
 * raw web socket implicitly (see below).
 *
 * The last one is a bit peculiar: web sockets have no "reopen"
 * method, so after every "close", the object has to be reconstructed.
 * Therefore, the service has to be a IRawWebSocket constructor
 * factory that yields web socket constructors rather than web socket
 * objects.
 */
export var factoryIService = (
    adhConfig : AdhConfig.IService,
    constructRawWebSocket : (uri) => IRawWebSocket
) : IService => {
    "use strict";

    /**
     * the socket handle
     */
    var _ws : IRawWebSocket;

    /**
     * a distionary of all callbacks, stored under their
     * resp. resources.
     */
    var _subscriptions : Subscriptions;

    /**
     * same type as _subscriptions, but these are still waiting for
     * being sent over the wire.  this is necessary because when _ws
     * is initialized and the adhWebSocket handle returned to the consumer,
     * the consumer may start subscribing to stuff, but the web socket
     * is not in connected state yet.
     *
     * FIXME: this could be better implemented with $q: if not
     * connected, check if _pendingSubscriptions contains a deferred
     * promise, and if it does not, create one.  call .then(..) on the
     * promise with what you want to do once the connection is
     * established; in the .onconnect(..) callback, fulfill the
     * promise and delete _pendingSubscriptions.
     */
    var _pendingSubscriptions : Subscriptions;

    /**
     * request queue.  we append all requests to the end of this list,
     * and pop them from the beginning as the responses come in.
     * rationale: "ok" responses contain a copy of the request data,
     * but "error" responses do not (the request may have been broken
     * json and not contain any valid data).  so it is necessary to
     * rely on the responses coming back in the same order in which
     * the frontend send the requests.
     */
    var _requests : Request[] = [];


    /**
     * function declarations
     */

    var register : (path : string, callback : (event : IServerEvent) => void) => string;
    var unregister : (path : string, id : string) => void;
    var sendRequest : (req : Request) => void;
    var handleResponseMessage : (msg : ServerMessage) => void;

    var onmessage : (event : {data : string }) => void;
    var onerror : (event : any) => void;
    var onopen : (event : any) => void;
    var onclose : (event : any) => void;

    var open : () => any;

    // FIXME: all of the above should be testable, but are local
    // definitions in the factory function body.  rethink the factory
    // idiom!  perhaps using a class constructor instead would allow
    // to access instance methods in tests while instance methods
    // still have access to local state?  (do we even want that?)

    /**
     * register a new callback asynchronously (to _subscriptions if
     * connected; to _pendingSubscription otherwise).  if one is
     * already registered, crash.
     */
    register = (
        path : string,
        callback : (event : IServerEvent) => void
    ) : string => {
        console.log("register", path);
        if (_ws.readyState === _ws.OPEN) {
            return _subscriptions.add(path, callback, null, () => sendRequest({action: "subscribe", resource: path}));
        } else {
            return _pendingSubscriptions.add(path, callback);
        }
    };

    /**
     * unregister callback.  if it is not registered, crash.
     */
    unregister = (
        path : string,
        id : string
    ) : void => {
        console.log("unregister", path);
        if (!(_subscriptions.alive(path, id) || _pendingSubscriptions.alive(path, id))) {
            throw "WebSocket: unsubscribe: no subscription for " + JSON.stringify(path) + "!";
        } else {
            _subscriptions.del(path, id, () => {
                if (_ws.readyState === _ws.OPEN) {
                    sendRequest({action: "unsubscribe", resource: path});
                }
                // the case that _ws is not OPEN is silently ignored: the
                // server is expected to have forgotten anyway.
            });
            _pendingSubscriptions.del(path, id);
        }
    };

    /**
     * Send Request object (subscribe or unsubscribe); push it to
     * _requests; do some exception handling and logging.
     */
    sendRequest = (
        req : Request
    ) : void => {
        var reqString : string = JSON.stringify(req);
        console.log("WebSocket: sending " + JSON.stringify(req, null, 2));  // FIXME: introduce a log service for this stuff.

        if (_ws.readyState !== _ws.OPEN) {
            throw "WebSocket: attempt to write to non-OPEN websocket!";
        } else {
            _ws.send(reqString);
            _requests.push(req);
        }
    };

    /**
     * handle responses to requests
     *
     * if message is not an event, remove the matching request from
     * the queue and check for errors (server or client, user or
     * internal).
     */
    handleResponseMessage = (msg : ServerMessage) : void => {
        var req : Request = _requests.shift();

        // ResponseOk: request successfully processed!
        if (msg.hasOwnProperty("status")) {
            var checkCompare = (req : Request, resp : ResponseOk) => {
                if (req.action !== resp.action || req.resource !== resp.resource) {
                    throw ("WebSocket: onmessage: response does not match request!\n"
                           + req.action + " " + req.resource + "\n"
                           + resp.action + " " + resp.resource);
                }
            };

            var checkRedundant = (resp : ResponseOk) => {
                throw ("WebSocket: onmessage: received 'redundant' response.  this should not happen!\n"
                       + resp.toString());
            };

            switch (msg.status) {
            case "ok":
                checkCompare(req, msg);
                break;

            case "redundant":
                checkCompare(req, msg);
                checkRedundant(msg);
                break;
            }
        }

        // ResponseError: request failed!
        if (msg.hasOwnProperty("error")) {
            switch (msg.error) {
            case "unknown_action":
            case "unknown_resource":
            case "malformed_message":
            case "invalid_json":
            case "subscribe_not_supported":
            case "internal_error":
                throw ("WebSocket: onmessage: received error message.\n"
                       + msg.error + "\n"
                       + req.toString() + "\n"
                       + msg.toString());

            default:
                throw ("WebSocket: onmessage: received **unknown** error message.  this should not happen!\n"
                       + msg.error + "\n"
                       + req.toString() + "\n"
                       + msg.toString());
            }
        }
    };

    onmessage = (event : {data : string}) : void => {
        var msg : ServerMessage = JSON.parse(event.data);
        console.log("WebSocket: onmessage:"); console.log(JSON.stringify(msg, null, 2));  // FIXME: introduce a log service for this stuff.

        // ServerEvent: something happened to the backend data!
        if (msg.hasOwnProperty("event")) {
            _subscriptions.notify(msg);
        } else {
            handleResponseMessage(msg);
        }
    };

    onerror = (event) => {
        console.log("WebSocket: error!");
        console.log(JSON.stringify(event, null, 2));
        throw "WebSocket: error!";
    };

    onopen = (event) => {
        _pendingSubscriptions.forAll((path, id, callback) => {
            _subscriptions.add(path, callback, id, () => sendRequest({action: "subscribe", resource: path}));
            _pendingSubscriptions.del(path, id);
        });
    };

    onclose = (event) => {
        // _ws = open();

        console.log("WebSocket: close!  (see source code for things to fix here.)");
        console.log(JSON.stringify(event, null, 2));

        // FIXME: this is bad because it invalidates all previous
        // subscriptions, but adhWebSocket is not aware of that.
        //
        // if you fix this, also check unsubscribe (currently if
        // called in unconnected state, it clears out _subscriptions
        // and _pendingSubscriptions and just assumes the server has
        // unsusbcribed everything already.

        throw "WebSocket: close!";
    };

    open = () => {
        var _ws = constructRawWebSocket(adhConfig.ws_url);

        _ws.onmessage = onmessage;
        _ws.onerror = onerror;
        _ws.onopen = onopen;
        _ws.onclose = onclose;

        var createCallbackId = (() => {
            var x : number = 0;
            return () => (x++).toString();
        })();

        _subscriptions = new Subscriptions(createCallbackId);
        _pendingSubscriptions = new Subscriptions(createCallbackId);

        return _ws;
    };

    /**
     * (main)
     */
    _ws = open();

    return {
        register: register,
        unregister: unregister
    };
};

/**
 * trivial IRawWebSocket constructor factory that returns the built-in
 * thing.  (replace this for unit testing.)
 */
export var factoryIRawWebSocket = () => ((uri : string): IRawWebSocket => new WebSocket(uri));

export var factoryDummyWebSocket = () => ((uri : string): IRawWebSocket => {
    return {
        send: (msg) => undefined,
        onmessage: (event) => undefined,
        onerror: (event) => undefined,
        onopen: (event) => undefined,
        onclose: (event) => undefined,
        readyState: undefined,
        CONNECTING: undefined,
        OPEN: undefined,
        CLOSING: undefined,
        CLOSED: undefined
    };
});

/**
 * factory for export to consumer modules.  it combines
 * factoryIRawWebSocket and factoryIService in the way it is almost
 * always used (besides in unit tests).
 */
export var factory = (Modernizr : ModernizrStatic, adhConfig : AdhConfig.IService) : IService => {
    var websocketService;
    if (Modernizr.websockets) {
        websocketService = factoryIRawWebSocket();
    } else {
        console.log("Using dummy websocket service due to browser incapability.");
        websocketService = factoryDummyWebSocket();
    }
    return factoryIService(adhConfig, websocketService);
};


//////////////////////////////////////////////////////////////////////
// Widgets

/**
 * test widget
 */

interface WebSocketTestScope extends ng.IScope {
    messages : ServerMessage[];
    rawPaths : string;
}


/**
 * A simple test widget that dumps all relevant messages coming in
 * over the web socket to <pre> elements in the UI.
 */
export class WebSocketTest {

    public createDirective = ($timeout : ng.ITimeoutService, adhConfig : AdhConfig.IService, adhWebSocket : IService) : ng.IDirective => {
        var _self = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/WebSocketTest.html",
            scope: {
                rawPaths: "@paths"
            },
            transclude: true,
            controller: ["$scope", "$timeout", ($scope : WebSocketTestScope) => {
                $scope.messages = [];
                var paths = JSON.parse($scope.rawPaths);
                paths.map((path) => {
                    adhWebSocket.register(path, (serverEvent) => $scope.messages.push(serverEvent));
                });
            }]
        };
    };
}


/**
 * A button that is inactive as long as no changes are reported.  If a
 * change message is recieved via the web socket, the button is
 * activated and changes its appearance.  Incoming change messages are
 * collected and can be used in the rendering of the button (e.g. for
 * the message "there are N changes").  On button click, an angular
 * event is sent to all registered scopes.
 */

/*
export class WebSocketTrackerButton {
    ...
}

*/
