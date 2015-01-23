/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import _ = require("lodash");

import AdhWebSocket = require("../WebSocket/WebSocket");

export interface IHttpCacheItem {
    wshandle : number;
    promises : {[query : string] : ng.IPromise<any>};
}


/**
 * HTTP Cache Service
 *
 * This implements a cache which allows to store and automatically invalidate
 * imported HTTP responses.
 *
 * It is currently very much tied to the requirements of the HTTP responses.
 */
export class Service {
    "use strict";

    private cache;
    private debug = false;

    constructor(
        private adhWebSocket : AdhWebSocket.Service,
        private DSCacheFactory
    ) {
        this.setupCache(DSCacheFactory, adhWebSocket);
    }

    private setupCache(DSCacheFactory, adhWebSocket) {
        this.cache = DSCacheFactory("httpCache", {
            capacity: 10000,  // items
            maxAge: 5 * 60 * 1000,  // milliseconds
            deleteOnExpire: "aggressive",
            recycleFreq: 5000, // milliseconds
            onExpire: (key, value) => {
                this.adhWebSocket.unregister(key, value.wshandle);
            }
        });


        adhWebSocket.addEventListener("close", (msg) => {
            this.invalidateAll();
        });
    }

    private isConnected() {
        return this.adhWebSocket.isConnected();
    }

    public invalidate(path : string) : void {
        if (this.isConnected()) {
            var cached = this.cache.get(path);
            if (typeof cached !== "undefined") {
                this.adhWebSocket.unregister(path, cached.wshandle);
                this.cache.remove(path);
                if (this.debug) { console.log("invalidate: " + path); };
            }
        }
    }

    public invalidateAll() : void {
        if (this.isConnected()) {
            _.forEach(this.cache.keys(), (key : string) => {
                this.invalidate(key);
            });
        }
    }

    private getOrSetCached(path : string) : IHttpCacheItem {
        var cached = this.cache.get(path);
        if (typeof cached === "undefined") {
            var wshandle = this.adhWebSocket.register(path, (msg) => {
                this.invalidate(path);
            });
            cached = {
                wshandle: wshandle,
                promises: {}
            };
            this.cache.put(path, cached);
        }
        return cached;
    }

    public memoize(path, subkey, closure) {
        if (this.isConnected()) {
            var cached = this.getOrSetCached(path);

            var promise = cached.promises[subkey];
            if (typeof promise === "undefined") {
                if (this.debug) { console.log("cache miss: " + path + " " + subkey); };
                promise = closure();
                cached.promises[subkey] = promise;
            } else {
                if (this.debug) { console.log("cache hit: " + path + " " + subkey); };
            }
            return promise;
        } else {
            return closure();
        }
    }
}
