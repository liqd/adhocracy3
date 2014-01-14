/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");


// cache
//
// this module provides an api that lets you
//
//   - store objects locally in memory
//   - track expire notifications via web socket
//   - maintain both a working copy and a pristine copy of server state
//   - diff working copy and pristine copy
//   - commit working copy of one object
//   - batch commit of a sequence of objects
//   - store on disk (persistence)
//   - store commits indefinitely in case server is unavailable and sync after offline periods
//
// libraries for caching (we are using 1. for now) -
//
//  1. the angular-builtin $cacheFactory (leaves all the
//     adhocracy-specific stuff to us without trying to guess how it's
//     done.)
//
//  2. github.com/jmdobry/angular-cache (a lot of this is about
//     expiration time guessing, whereas we want to be explicit about
//     what expires and what lives.  but it also supports local
//     storage.)
//
//  3. http://gregpike.net/demos/angular-local-storage/demo/demo.html
//     (writes to disk, which is also interesting.)


// (cache size is taylored for testing: small enough to make test
// suite trigger overflow, big enough for other interesting things to
// happen.)
var cacheSizeInObjects = 7;


// service interface

export interface IService {
    get          : (path : string,                      update : (obj: Types.Content) => void) => void;
    put          : (path : string, obj : Types.Content, update : (obj: Types.Content) => void) => void;
    subscribe    : (path : string,                      update : (obj: Types.Content) => void) => number;
    unsubscribe  : (path : string, ix : number)                                                => void;
    commit       : (path : string,                      update : (obj: Types.Content) => void) => void;
    reset        : (path : string,                      update : (obj: Types.Content) => void) => void;
    destroy      : ()                                                                          => void;
}


// ICacheItem and helpers

interface ICacheItem {
    pristine       : Types.Content;
    working        : Types.Content;
    subscriptions  : Object;
    freshName      : () => number;
}

// Create item with undefined pristine and working copy.
// Subscriptions map is empty; freshName is initialized to start
// counding at 0.
function createEmptyItem(cache : ng.ICacheObject, path : string) : ICacheItem {
    function freshNamer() : () => number {
        var x : number = 0;
        return () => { x++; return x; };
    }

    var item : ICacheItem = {
        pristine: undefined,
        working: undefined,
        subscriptions: {},
        freshName: freshNamer(),
    };

    cache.put(path, item);
    return item;
}

// Overwrite woth pristine and working copy with arg.  Working copy is
// a reference to the arg, pristine is a deep copy.  Update the
// working copy simply by updating the object you passed to this
// function.  item must not be undefined.
function resetBoth(item : ICacheItem, obj : Types.Content) : void {
    if (typeof obj === "undefined" || typeof item === "undefined") {
        console.log("internal error.");
        throw "died";
    }

    item.working = obj;
    item.pristine = Util.deepcp(obj);
}

function registerUpdater(item : ICacheItem, update : (obj: Types.Content) => void) : number {
    if (typeof item === "undefined" || typeof update === "undefined") {
        console.log("internal error.");
        throw "died";
    }

    var ix = item.freshName();
    item.subscriptions[ix] = update;
    return ix;
}

function unregisterUpdater(path : string, item : ICacheItem, ix : number) : void {
    if (typeof item === "undefined") {
        console.log("attempt to unsubscribe unregistered path: ", path, ix);
    } else {
        if (!(ix in item.subscriptions)) {
            console.log("attempt to unsubscribe unregistered index: ", path, ix);
        } else {
            delete item.subscriptions[ix];
        }
    }
}

function updateAll(item : ICacheItem) : void {
    var obj = item.working;
    if (typeof obj === "undefined" || typeof item === "undefined") {
        console.log("internal error.");
        throw "died";
    }

    for (var ix in item.subscriptions) {
        item.subscriptions[ix](obj);
    }
}

// Overwrite working copy with pristine.  item must not be undefined.
function resetWorking(item : ICacheItem) : void {
    var obj = item.pristine;
    if (typeof obj === "undefined" || typeof item === "undefined") {
        console.log("internal error.");
        throw "died";
    }

    item.pristine = Util.deepcp(obj);
    item.working = obj;
}


// factory

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService {
    var cache : ng.ICacheObject = $cacheFactory("1", { capacity: cacheSizeInObjects });
    var ws : AdhWS.IService = AdhWS.factory(adhHttp);


    // lookup object in cache.  in case of miss, retrieve the object
    // and add it to the cache.  call callback once immediately, then
    // discard the callback.
    function get(path : string, update : (obj: Types.Content) => void) : void {
        var item : ICacheItem = cache.get(path);

        if (typeof item === "undefined") {
            console.log("cache miss!");
            item = createEmptyItem(cache, path);
            getAndWatch(item, path, update);
        } else {
            console.log("cache hit!");
            update(item.working);
        }
    }

    // FIXME: document!
    function put(path : string, obj : Types.Content, update : (obj: Types.Content) => void) : void {
        var item : ICacheItem = cache.get(path);

        if (typeof item === "undefined") {
            console.log("cache miss!");
            item = createEmptyItem(cache, path);

            // FIXME: post this to server immediately; on success,
            // update working copy and initialize pristine copy.

            // FIXME: what happens if somebody works on the object
            // while it's still going to the server?

        } else {
            console.log("cache hit!");

            // FIXME: see if we need to create a new version or
            // overwrite old object (extend http for the latter, and
            // probably the case distinction should also go there).
            // notify server immediately; on success, update item and
            // call update callback.

        }
    }

    // lookup object in cache.  in case of miss, retrieve the object
    // add it to the cache, and register item with the ws service
    // (which calls the updater once immediately).  updater callback
    // will be registered in the cache item and called once
    // immediately.  returns a (numeric) subscription handle.
    function subscribe(path : string, update : (obj: Types.Content) => void) : number {
        var item : ICacheItem = cache.get(path);
        var ix : number;

        if (typeof item === "undefined") {
            console.log("cache miss!");
            item = createEmptyItem(cache, path);
            ix = registerUpdater(item, update);
            getAndWatch(item, path);
        } else {
            console.log("cache hit!");
            update(item.working);
            ix = registerUpdater(item, update);
        }

        return ix;

        // if we had to return a promise from this function, and
        // had to construct one from the promised value, this is
        // what we could do:
        //
        //   return $q.defer().promise.then(function() { return item; });
        //
        // (just leaving this in because it's so pretty :-)
    }

    // remove subscription from cache item.  ix is the subscription
    // handle that was returned by subscribe.
    function unsubscribe(path : string, ix : number) : void {
        var item = cache.get(path);
        unregisterUpdater(path, item, ix);
    }

    // FIXME: document this!
    function commit(path : string) : void {
        var item : ICacheItem = cache.get(path);

        // if path is invalid, crash.
        if (typeof item === "undefined") {
            console.log("unknown path: " + path);
            throw "died";
        }

        // if working copy is unchanged, do nothing.
        if (!Util.deepeq(item.pristine, item.working)) {
            // otherwise, post working copy and overwrite pristine with
            // new version from server.  (must be from server, since
            // server changes things like version successor and
            // predecessor edges.)
            //
            // when object is retrieved and cached, notify application of
            // the update.  (necessary in case the server changed the
            // object in a way relevant to the UI, e.g. by adding an
            // update timestamp.)
            adhHttp.postNewVersion(path, item.working, (obj) => {
                resetBoth(item, obj);
                updateAll(item);
                return obj;
            });
        }
    }

    // FIXME: document this!
    function reset(path : string) : void {
        var item : ICacheItem = cache.get(path);

        if (typeof item === "undefined") {
            console.log("invalid path: " + path);
            throw "died";
        } else {
            resetWorking(item);
            updateAll(item);
        }
    }

    function destroy() {
        ws.destroy();
        cache.destroy();
    }

    // Fetch obj asynchronously from server.  Initialize item with
    // pristine and working copy, call all registered updaters once,
    // and then call updateOnce parameter once and discard it.
    // Register web socket listener callback that call registered
    // updaters on every server update notification.  If server sends
    // an update notifcation, but subscription map is empty, the
    // listener callback removes the item from cache.
    function getAndWatch(item : ICacheItem,
                         path : string,
                         updateOnce ?: (obj : Types.Content) => void) : void
    {
        if (typeof cache === "undefined" || typeof ws === "undefined" || typeof item === "undefined") {
            console.log("internal error.");
            throw "died";
        }

        function syncFirst(obj : Types.Content) {
            resetBoth(item, obj);
            updateAll(item);

            if (typeof updateOnce !== "undefined") {
                updateOnce(obj);
            }
        }

        function syncThen(obj : Types.Content) {
            if (Object.keys(item.subscriptions).length === 0) {
                ws.unsubscribe(path);
                cache.remove(path);
            } else {
                resetBoth(item, obj);
                updateAll(item);
            }

            // FIXME: make sure there is no concurrency issue here: what
            // if the update callback is already queued, but then the item
            // is removed from cache?
        }

        adhHttp.get(path).then((obj : Types.Content) : void => {
            syncFirst(obj);
            ws.subscribe(path, syncThen);
        });
    }

    return {
        get: get,
        put: put,
        subscribe: subscribe,
        unsubscribe: unsubscribe,
        commit: commit,
        reset: reset,
        destroy: destroy,
    };
}



// TODO:
//
//   - commit working copy of one object
//   - think about concurrent sanity of commit, reset (what if pristine changes while user changes working copy?)
//   - batch commit of a sequence of objects
//
//   - limit cache size, i.e. expire objects.  (what does that mean
//   - for pristine vs. working copy objects?  we can probably only
//   - expire unsubscribed objects.  note that in that sense, objects
//   - retrieved with 'get' are also subscribed!)
//
//   - leave object in cache and web socket open if it is unsubscribed
//     from app.  web socket update notifcations change meaning: if
//     subscribed from app, update; if not, drop from cache.
//
//   - store on disk
//   - store commits indefinitely in case server is unavailable and sync after offline periods
