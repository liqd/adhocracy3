/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");


// FIXME: all comments in this module may be out of sync.  check and, if necessary, rewrite!


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
    get          : (path : string,                      subscribe : boolean, update : (obj: Types.Content) => void) => number;
    put          : (path : string, obj : Types.Content, subscribe : boolean, update : (obj: Types.Content) => void) => number;
    unsubscribe  : (path : string, ix : number)                                                                     => void;
    commit       : (path : string,                      update : (obj: Types.Content) => void)                      => void;
    reset        : (path : string,                      update : (obj: Types.Content) => void)                      => void;
    destroy      : ()                                                                                               => void;
}


// ICacheItem and helpers

interface ICacheItem {
    pristine       : Types.Content;
    working        : Types.Content;
    subscriptions  : Object;
    freshName      : () => number;
}


// factory

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService
{
    //////////////////////////////////////////////////////////////////////
    // private state

    var cache : ng.ICacheObject = $cacheFactory("1", { capacity: cacheSizeInObjects });
    var ws : AdhWS.IService = AdhWS.factory(adhHttp);



    //////////////////////////////////////////////////////////////////////
    // public api

    // lookup object in cache.  in case of miss, retrieve the object
    // and add it to the cache.  call callback once immediately with a
    // reference to the working copy as argument, then discard the
    // callback.  if the subscribe flag is true, keep the referenced
    // working copy in sync with server updates.
    function get(path : string, subscribe : boolean, bindModel : (obj: Types.Content) => void) : number {
        var item : ICacheItem = cache.get(path);
        var ix : number;

        if (typeof item === "undefined") {
            item = createEmptyItem(path);
            if (subscribe) {
                ix = registerSubscription(item);
                adhHttp.get(path).then(initItem(item, path, bindModel));
            } else {
                adhHttp.get(path).then(initItem(item, path, (obj) => { bindModel(Util.deepcp(obj)); }));
            }
        } else {
            if (subscribe) {
                ix = registerSubscription(item);
                bindModel(item.working);
            } else {
                bindModel(Util.deepcp(item.working));
            }
        }

        return ix;
    }

    // FIXME: document!
    function put(path : string, obj : Types.Content, subscribe : boolean, bindModel : (obj: Types.Content) => void) : number {
        var item : ICacheItem = cache.get(path);
        var ix : number;

        if (typeof item === "undefined") {
            item = createEmptyItem(path);
            if (subscribe) {
                ix = registerSubscription(item);
                adhHttp.put(path, obj).then(initItem(item, path, bindModel));
            } else {
                adhHttp.put(path, obj).then(initItem(item, path, (obj) => { bindModel(Util.deepcp(obj)); }));
            }
        } else {
            throw "put on existing objects not implemented";

            // FIXME: see if we need to create a new version or
            // overwrite old object (extend http for the latter, and
            // probably the case distinction should also go there).
        }

        return ix;
    }

    // remove subscription from cache item.  ix is the subscription
    // handle that was returned by subscribe.
    function unsubscribe(path : string, ix : number) : void {
        unregisterSubscription(path, cache.get(path), ix);
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
        }
    }

    function destroy() {
        ws.destroy();
        cache.destroy();
    }



    //////////////////////////////////////////////////////////////////////
    // private helper functions

    // Create item with undefined pristine and working copy.
    // Subscriptions map is empty; freshName is initialized to start
    // counding at 0.
    function createEmptyItem(path : string) : ICacheItem {
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

    // Fetch obj asynchronously from server.  Initialize item with
    // pristine and working copy, call all registered updaters once,
    // and then call updateOnce parameter once and discard it.
    // Register web socket listener callback that call registered
    // updaters on every server update notification.  If server sends
    // an update notifcation, but subscription map is empty, the
    // listener callback removes the item from cache.
    function initItem(item : ICacheItem,
                      path : string,
                      bindModel : (obj : Types.Content) => void) : (obj : Types.Content) => void
    {
        return (obj : Types.Content) => {
            resetBoth(item, obj);
            bindModel(obj);

            ws.subscribe(path, (obj) => {

                // FIXME: at this point, ws has already retrieved the
                // updated obj, and only then do we check whether
                // anybody is still interested.  ws should give us the
                // choice whether to get the update or drop the
                // obsolete item from the cache before that happens.

                if (Object.keys(item.subscriptions).length === 0) {
                    ws.unsubscribe(path);
                    cache.remove(path);
                } else {
                    resetBoth(item, obj);
                }

                // FIXME: make sure there is no concurrency issue here: what
                // if the update callback is already queued, but then the item
                // is removed from cache?
            });
        };
    }

    // Overwrite woth pristine and working copy with arg.  Working copy is
    // a reference to the arg, pristine is a deep copy.  Update the
    // working copy simply by updating the object you passed to this
    // function.  item must not be undefined.
    function resetBoth(item : ICacheItem, obj : Types.Content) : void {
        Util.deepoverwrite(obj, item.working);
        item.pristine = Util.deepcp(obj);
    }

    // Overwrite working copy with pristine.  item must not be undefined.
    function resetWorking(item : ICacheItem) : void {
        Util.deepoverwrite(item.pristine, item.working);
    }

    function registerSubscription(item : ICacheItem) : number {
        var ix = item.freshName();
        item.subscriptions[ix] = true;
        return ix;
    }

    function unregisterSubscription(path : string, item : ICacheItem, ix : number) : void {
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


    //////////////////////////////////////////////////////////////////////
    // compose cache object

    return {
        get: get,
        put: put,
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
