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

export interface IService {
    get          : (path : string, update : (obj: Types.Content) => void) => void;
    commit       : (path : string, update : (obj: Types.Content) => void) => void;
    reset        : (path : string, update : (obj: Types.Content) => void) => void;
    subscribe    : (path : string, update : (obj: Types.Content) => void) => void;
    unsubscribe  : (path : string, strict ?: boolean)                     => void;
    destroy      : ()                                                     => void;
}

interface CacheItem {
    pristine  : Types.Content;
    working   : Types.Content;
}

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService {
    var cache : ng.ICacheObject = $cacheFactory("1", { capacity: cacheSizeInObjects });
    var ws = AdhWS.factory(adhHttp);

    // lookup object in cache can call callback once immediately on
    // arrival of the object.
    //
    // in case of cache miss, retrieve and add it.  register an update
    // callback with its path that removes it from the cache if the
    // server sends an expiration notification.
    function get(path : string, update : (obj: Types.Content) => void) : void {
        var item : CacheItem = cache.get(path);

        if (typeof item !== "undefined") {
            console.log("cache hit!");
            resetWorking(cache, path);
            update(item.working);
        } else {
            console.log("cache miss!");
            adhHttp.get(path).then(obj => {
                createItem(cache, path, obj);
                update(obj);
                ws.subscribe(path, (obj) => unsubscribe(path));
            });
        }
    }

    // FIXME: document!
    function commit(path : string, update : (obj: Types.Content) => void) : void {
        var item : CacheItem = cache.get(path);

        // if path is invalid, crash.
        if (typeof item === "undefined") {
            console.log("unknown path: " + path);
            throw "died";
        }

        // if working copy is unchanged, do nothing.
        if (Util.deepeq(item.pristine, item.working)) {
            return;
        }

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
            createItem(cache, path, obj);
            update(obj);
            return obj;
        });
    }

    // FIXME: document!
    function reset(path : string, update : (obj: Types.Content) => void) : void {
        var item : CacheItem = cache.get(path);
        if (typeof item === "undefined") {
            console.log("invalid path: " + path);
            throw "died";
        } else {
            resetWorking(cache, path);
            update(item.working);
        }
    }

    // lookup object in cache and call callback once immediately and
    // once on every update from the server, until unsubscribe is
    // called on this path.
    //
    // in case of miss, retrieve and add it.  register update callback
    // on its path.  the callback is called once now and then every
    // time the object is updated in cache, until unsubscribe is
    // called on this path.
    function subscribe(path : string, update : (n: Types.Content) => void) : void {

        var item = cache.get(path);

        if (typeof item !== "undefined") {
            console.log("cache hit!");
            createItem(cache, path, item);
            update(item.working);

            // if we had to return a promise from this function, and
            // had to construct one from the promised value, this is
            // what we could do:
            //
            //   return $q.defer().promise.then(function() { return item; });
            //
            // (just leaving this in because it's so pretty :-)
        } else {
            console.log("cache miss!");
            adhHttp.get(path).then((obj : Types.Content) : void => {
                createItem(cache, path, obj);
                ws.subscribe(path, update);
                update(obj);
            });
        }
    }

    function unsubscribe(path : string) : void {
        ws.unsubscribe(path);
        cache.remove(path);

        // FIXME: make sure there is no concurrency issue here: what
        // if the update callback is already queued, but then the
        // item is removed from cache?  won't that trigger a reload,
        // and thus waste network and cache resources?
    }

    function destroy() {
        ws.destroy();
        cache.destroy();
    }

    return {
        get: get,
        commit: commit,
        reset: reset,
        subscribe: subscribe,
        unsubscribe: unsubscribe,
        destroy: destroy,
    };
}



// Overwrite pristine copy.  This must only be done with content data
// retrieved from the server.  Throw an exception if get yields
// nothing.
function updatePristine(cache : ng.ICacheObject, path : string, obj : Types.Content) : void {
    var item : CacheItem = cache.get(path);

    if (typeof item === "undefined") {
        console.log("nothing found at " + path);
        throw "died";
    } else {
        item.pristine = obj;
    }
}

// Overwrite working copy with pristine.  Throw an exception if get
// yields nothing.
function resetWorking(cache : ng.ICacheObject, path : string) : void {
    var item : CacheItem = cache.get(path);

    if (typeof item === "undefined") {
        console.log("nothing found at " + path);
        throw "died";
    } else {
        item.working = item.pristine;
        item.pristine = Util.deepcp(item.working);
    }
}

// Overwrite woth pristine and working copy with arg.  Working copy is
// a reference to the arg, pristine is a deep copy.  Update the
// working copy simply by updating the object you passed to this
// function.
function createItem(cache : ng.ICacheObject, path : string, obj : Types.Content) : CacheItem {
    var item : CacheItem = { pristine: Util.deepcp(obj), working: obj };

    cache.put(path, item);
    return item;
}

// Check if object differs between pristine and working copy.  Throws
// an exception if get yields nothing.
function workingCopyChanged(cache : ng.ICacheObject, path : string) : boolean {
    var item : CacheItem = cache.get(path);

    if (typeof item === "undefined") {
        console.log("nothing found at " + path);
        throw "died";
    } else {
        return item.working !== item.pristine;
    }
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
