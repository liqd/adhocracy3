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

import AdhConfig = require("./Config");


export interface IMessage {
    data : IMessageData;
    name : string;
}

export interface IMessageData {
    embedderOrigin? : string;
}

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

    constructor(public _postMessage : IPostMessageService, public $window, public $rootScope) {
        var _self : Service = this;

        _self.registerMessageHandler("setup", _self.setup.bind(_self));
        _self.manageResize();

        _self.postMessage("requestSetup", {});
    }

    public registerMessageHandler(name, callback) {
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

    public postResize(height) {
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


export var factory = (adhConfig : AdhConfig.Type, $window, $rootScope) : IService => {
    if (adhConfig.embedded) {
        var postMessageToParent = $window.parent.postMessage.bind($window.parent);
        return new Service(postMessageToParent, $window, $rootScope);
    } else {
        return new Dummy();
    }
};
