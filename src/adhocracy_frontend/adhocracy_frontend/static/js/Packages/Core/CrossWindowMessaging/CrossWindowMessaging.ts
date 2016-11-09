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
 * name: "resize"  // from SDK to iframes
 * data: {
 *   height: number
 * }
 *
 * name: "requestSetup"  // from SDK to iframes
 * data: {}
 *
 * name: "setup"  // sent from SDK to iframes
 * data: {
 *   embedderOrigin: string
 * }
 *
 * Message handler callbacks for to-iframes messages are registered by
 * the service factory.
 *
 * Messages are serialized with JSON.stringify before being sent via
 * window.postMessage().  (Reason: browser compatibility; IE prior to
 * 10 in particular, but others may be affected.)
 */

/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as _ from "lodash";

import * as AdhConfig from "../Config/Config";
import * as AdhCredentials from "../User/Credentials";
import * as AdhUser from "../User/User";


export interface IMessage {
    data : IMessageData;
    name : string;
}

export interface IMessageData {
    embedderOrigin? : string;
    height? : number;
    token? : string;
    userPath? : string;
    userData? : any;
    url? : string;
}

export interface ICallback {
    name : string;
    callback : (data : IMessageData) => void;
}

export interface IPostMessageService {
    (data : string, origin : string) : void;
}

export interface IService {
    on : (name : string, callback : (data : IMessageData) => void) => () => void;
    postResize : (height : number) => void;
    dummy? : boolean;
}

export class Provider implements angular.IServiceProvider {
    public $get;
    private callbacks : ICallback[] = [];

    constructor() {
        var _self = this;
        this.$get = ["adhConfig", "$location", "$window", "$rootScope", "adhCredentials", "adhUser", (
            adhConfig : AdhConfig.IService,
            $location : angular.ILocationService,
            $window : Window,
            $rootScope,
            adhCredentials : AdhCredentials.Service,
            adhUser : AdhUser.Service
        ) : IService => {
            if (adhConfig.embedded) {
                var postMessageToParent = $window.parent.postMessage.bind($window.parent);
                return new Service(
                    postMessageToParent,
                    $location,
                    $window,
                    $rootScope,
                    adhConfig.trusted_domains,
                    adhCredentials,
                    adhUser,
                    _self.callbacks);
            } else {
                return new Dummy();
            }
        }];
    }

    public on(name : string, callback) {
        this.callbacks.push({
            name: name,
            callback: callback
        });
    }
}

export class Service implements IService {

    private embedderOrigin : string = "*";

    constructor(
        private _postMessage : IPostMessageService,
        private $location : angular.ILocationService,
        private $window : Window,
        private $rootScope,
        private trustedDomains : string[],
        private adhCredentials : AdhCredentials.Service,
        private adhUser : AdhUser.Service,
        providedMessageHandlers : ICallback[] = []
    ) {
        var _self : Service = this;

        _self.on("setup", _self.setup.bind(_self));
        _self.on("setToken", _self.setToken.bind(_self));
        _self.on("deleteToken", _self.deleteToken.bind(_self));

        _self.manageResize();

        for (var messageHandler of providedMessageHandlers) {
            _self.on(messageHandler.name, messageHandler.callback);
        }

        _self.postMessage("requestSetup", {});
    }

    public on(name, callback) : () => void {
        var _self : Service = this;

        var wrapper = (event) => {
            var message = JSON.parse(event.data);

            if (((message.name === "setup") || (event.origin === _self.embedderOrigin)) && (message.name === name)) {
                callback(message.data);
            }
        };

        _self.$window.addEventListener("message", wrapper);
        return () => _self.$window.removeEventListener("message", wrapper);
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

    private setToken(data : IMessageData) : void {
        if (data.token && data.userPath) {
            this.adhCredentials.storeAndEnableToken(data.token, data.userPath);
        }
    }

    private deleteToken(data : IMessageData) :  void {
        this.adhCredentials.deleteToken();
    }

    private sendAuthMessages() {
        var _self : Service = this;

        return typeof _self.adhUser !== "undefined" && _.includes(_self.trustedDomains, _self.embedderOrigin);
    }

    private sendLoginState(loggedIn) {
        var _self : Service = this;

        if (_self.sendAuthMessages()) {
            // the case (loggedIn === undefined) doesn't trigger a message
            if (loggedIn === true) {
                _self.postMessage("login", {
                    token: _self.adhCredentials.token,
                    userPath: _self.adhCredentials.userPath,
                    userData: _self.adhUser.data
                });
            } else if (loggedIn === false) {
                _self.postMessage("logout", {});
            }
        }
    }

    private setup(data: IMessageData) : void {
        var _self : Service = this;
        var lastLoggedIn : boolean;

        if (_self.embedderOrigin === "*") {
            _self.embedderOrigin = data.embedderOrigin;

            if (typeof _self.adhUser !== "undefined") {
                _self.adhUser.ready.then(() =>
                    _self.$rootScope.$watch(() => typeof _self.adhUser.data !== "undefined", (loggedIn) => {
                        if (loggedIn !== lastLoggedIn) {
                            lastLoggedIn = loggedIn;
                            _self.sendLoginState(loggedIn);
                        }
                    }));
            }

            _self.$rootScope.$watch(() => _self.$location.absUrl(), (absUrl : string) => {
                _self.postMessage(
                    "urlchange",
                    {url: absUrl}
                );
            });
        }
    }

    /**
     * Body does not trigger resize events. So we have to guess when its height
     * has changed ourselves.
     *
     * The following options come to mind:
     *
     * 1. polling (check for changes on regular intervals using $interval)
     * 2. angular's $watch
     * 3. triggering a resize manually whenever we change something
     * 4. CSS hack: https://marcj.github.io/css-element-queries/
     *
     * This function uses 2. in combination with the window resize event to
     * also catch changes triggered by the embedder.
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

    public on(name, callback) {
        return () => null;
    }

    public postResize(height) {
        return;
    }
}
