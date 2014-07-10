/**
 * Cross Window Messaging
 *
 * Adhocracy -- or parts of it -- can be embedded as iframes.  The iframe provides
 * sufficient isolation to separate our own DOM, JavaScript and CSS from that of the
 * embedder page.
 *
 * Still it is required to be able to communicate between the embedder and the embedde.
 * On the embedee site, this is handled by this module.  On the embedder site it is most
 * likely handled by AdhocracySDK.
 *
 * Messages sent between the two are always of type IMessage.  Currentently the following
 * messages exists:
 *
 * name: "resize"
 * data: {
 *   height: number
 * }
 *
 * Messages are serialized with JSON.stringify before being sent via
 * window.postMessage().  (Reason: browser compatibility; IE prior to
 * 10 in particular, but others may be affected.)
 */

import AdhConfig = require("./Config");


export interface IMessage {
    data : IMessageData;
    name : string;
}

export interface IMessageData {}

export interface IPostMessageService {
    (data : string, origin : string) : void;
}

export interface IService {
    registerMessageHandler : (name : string, callback : (IMessageData) => void) => void;
    postResize : (height : number) => void;
    dummy? : boolean;
}


export class Service implements IService {

    private embedderOrigin : string = "*";
        // FIXME: this is a bit lax: all incoming message are taken
        // seriously (bad!), and all outgoing messages may end up in
        // the hands of hostile windows.  think of something more
        // sohpisticated!

    constructor(public _postMessage : IPostMessageService, public $window, public $interval) {
        var _self : Service = this;

        _self.manageResize();
    }

    public registerMessageHandler(name, callback) {
        var _self : Service = this;

        _self.$window.addEventListener("message", (event) => {
            var message = JSON.parse(event.data);

            if ((_self.embedderOrigin === "*" || event.origin === _self.embedderOrigin)
                && (message.name === name)) {
                callback(message.data);
            }
        });
    }

    private postMessage(name: string, data: IMessageData) : void {
        var _self : Service = this;

        var message : IMessage = {
            name: name,
            data: data
        };

        _self._postMessage(JSON.stringify(message), _self.embedderOrigin);
    }

    public postResize(height) {
        var _self : Service = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }

    /**
     * Body does not trigger resize events. So we have to guess when its height
     * has changed ourselves.
     */
    private manageResize() : void {
        var _self : Service = this;

        var postResizeIfChange = (() => {
            var oldHeight = 0;
            return () => {
                var height = _self.$window.document.body.clientHeight;
                if (height !== oldHeight) {
                    oldHeight = height;
                    _self.postResize(height);
                }
            };
        })();

        // Check for changes regulary
        _self.$interval(postResizeIfChange, 100);
    }
}


export class Dummy implements IService {
    public dummy : boolean;

    constructor() {
        this.dummy = true;
    }

    registerMessageHandler(name, callback) {
        return;
    }

    postResize(height) {
        return;
    }
}


export var factory = (adhConfig : AdhConfig.Type, $window, $interval) : IService => {
    if (adhConfig.embedded) {
        var postMessageToParent = $window.parent.postMessage.bind($window.parent);
        return new Service(postMessageToParent, $window, $interval);
    } else {
        return new Dummy();
    }
};
