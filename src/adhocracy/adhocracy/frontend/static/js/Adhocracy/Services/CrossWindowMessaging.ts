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
 * name: "requestSetup"
 * data: {}
 *
 * name: "setup"
 * data: {
 *   embedderOrigin: string
 * }
 *
 * Messages are serialized with JSON.stringify before being sent via
 * window.postMessage().  (Reason: browser compatibility; IE prior to
 * 10 in particular, but others may be affected.)
 */


export interface IMessage {
    data : IMessageData;
    name : string;
}


export interface IMessageData {
    embedderOrigin? : string;
}


export class Service {

    private embedderOrigin : string = "*";

    constructor(public _postMessage, public $window, public $interval) {
        var _self : Service = this;

        _self.registerMessageHandler("setup", _self.setup.bind(_self));
        _self.manageResize();

        _self.postMessage("requestSetup", {});
    }

    public registerMessageHandler(name : string, callback : (IMessageData) => void) : void {
        var _self : Service = this;

        _self.$window.addEventListener("message", (event) => {
            var message = JSON.parse(event.data);

            if (((message.name === "setup") || (event.origin === _self.embedderOrigin)) && (message.name === name)) {
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

    public postResize(height: number) : void {
        var _self : Service = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }

    private setup(data: IMessageData) : void {
        var _self : Service = this;

        if (_self.embedderOrigin === "*") {
            _self.embedderOrigin = data.embedderOrigin;
        }
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


export var factory = ($window, $interval) => {
    var postMessageToParent = (data, origin) => $window.parent.postMessage(data, origin);
    return new Service(postMessageToParent, $window, $interval);
};
