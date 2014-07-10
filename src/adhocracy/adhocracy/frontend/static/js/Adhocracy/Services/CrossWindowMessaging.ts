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


export interface IMessage {
    data : IMessageData;
    name : string;
}


export interface IMessageData {}


export class Service {

    private embedderOrigin : string = "*";
        // FIXME: this is a bit lax: all incoming message are taken
        // seriously (bad!), and all outgoing messages may end up in
        // the hands of hostile windows.  think of something more
        // sohpisticated!

    constructor(public _postMessage, public $window, public $rootScope) {
        var _self : Service = this;

        _self.manageResize();
    }

    public registerMessageHandler(name : string, callback : (IMessageData) => void) : void {
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

    public postResize(height: number) : void {
        var _self : Service = this;

        _self.postMessage(
            "resize",
            {height: height}
        );
    }

    /**
     * Body does not trigger resize events. So we have to guess when its height
     * has changed ourselves.
     *
     * The following options come to mind:
     *
     * - polling (check for changes on regular intervals using $interval)
     * - angular's $watch
     * - triggering a resize manually whenever we change something
     * - CSS hack: https://marcj.github.io/css-element-queries/
     */
    private manageResize() : void {
        var _self : Service = this;

        var getHeight = () : number => _self.$window.document.body.clientHeight;

        _self.$rootScope.$watch(getHeight, (height) => {
            _self.postResize(height);
        });
        _self.$window.addEventListener("resize", () => {
            _self.postResize(getHeight());
        });
    }
}


export var factory = ($window, $rootScope) => {
    var postMessageToParent = (data, origin) => $window.parent.postMessage(data, origin);
    return new Service(postMessageToParent, $window, $rootScope);
};
