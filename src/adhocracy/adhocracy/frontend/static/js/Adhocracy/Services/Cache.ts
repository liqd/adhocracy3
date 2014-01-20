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
//   - diff working copy (returned to application) and cached copy
//   - commit working copy
//   - batch commit of a sequence of objects
//   - store on disk (persistence)
//   - manage commits locally indefinitely in case server is unavailable and sync after offline periods
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
    get          : (path : string,                      subscribe : boolean, updateModel : (obj : Types.Content) => void) => number;
    put          : (path : string, obj : Types.Content, subscribe : boolean, updateModel : (obj : Types.Content) => void) => number;
    commit       : (path : string, obj : Types.Content) => boolean;
    unsubscribe  : (path : string, ix : number) => void;
    destroy      : () => void;
}


// internal cache item type.  contains pristine copy, a dict of
// subscribed callbacks that are invoked every time an update is
// received from the server via websocket, and a generator for fresh
// subscription handles.  (the working copy is returned via the
// updateModel callbacks as a deep copy and maintained by the service
// client)
interface ICacheItem {
    pristine       : Types.Content;
    subscriptions  : Object;  /* { <path> : <callack>, ... } */
    freshName      : () => number;
}


// factory

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService {

    //////////////////////////////////////////////////////////////////////
    // private state

    var cache : ng.ICacheObject = $cacheFactory("1", { capacity: cacheSizeInObjects });
    var ws : AdhWS.IService = AdhWS.factory(adhHttp);
    var tickms : number = 100;  // miliseconds between two checks for updates


    //////////////////////////////////////////////////////////////////////
    // public api

    // lookup object in cache.  in case of miss, retrieve the object
    // and add it to the cache.  call updateModel once immediately
    // after content is available with a deep copy of it.  if the
    // subscribe flag is true, call updateModel again emitting new
    // versions of the content every time the server sends an update.
    function get(path : string, subscribe : boolean, updateModel : (obj : Types.Content) => void) : number {
        var item : ICacheItem = cache.get(path);
        var ix : number;

        if (typeof item === "undefined") {
            item = createEmptyItem(path);

            if (subscribe) {
                ix = registerSubscription(item, updateModel);
            }

            adhHttp.get(path).then(initItem(item, path)).then((obj) => updateModel(Util.deepcp(obj)));
        } else {
            if (subscribe) {
                ix = registerSubscription(item, updateModel);
            }

            // FIXME: can $q do this more elegantly?
            function check() {
                if (typeof item.pristine === "undefined") {
                    setTimeout(check, tickms);
                } else {
                    updateModel(Util.deepcp(item.pristine));
                }
            }

            check();
        }

        return ix;
    }

    // a bit like get, but sends an object to the server first.  FIXME: document better.
    function put(path : string, obj : Types.Content, subscribe : boolean, updateModel : (obj : Types.Content) => void) : number {
        var item : ICacheItem = cache.get(path);
        var ix : number;

        if (typeof item === "undefined") {
            item = createEmptyItem(path);

            if (subscribe) {
                ix = registerSubscription(item, updateModel);
            }

            adhHttp.put(path, obj).then(initItem(item, path)).then((obj) => updateModel(Util.deepcp(obj)));
        } else {
            throw "put on existing objects not implemented";

            // FIXME: see if we need to create a new version or
            // overwrite old object (extend http for the latter, and
            // probably the case distinction should also go there).
        }

        return ix;
    }

    // if working copy is unchanged, do nothing.  otherwise, post
    // working copy and overwrite pristine with new version from
    // server.  (must be from server, since server changes things like
    // version successor and predecessor edges.)  returns a boolean
    // that states whether a new version was actually created.  if
    // path gives a cache miss, crash.
    function commit(path : string, obj : Types.Content) : boolean {
        var item : ICacheItem = cache.get(path);
        var workingCopyNew : boolean;

        if (typeof item === "undefined") {
            console.log("adhCache.commit: invalid path: " + path);
            throw "died";
        }

        workingCopyNew = !Util.deepeq(item.pristine, obj);
        if (workingCopyNew) {
            adhHttp.postNewVersion(path, obj);

            // that's all!  we don't need to update the cache item,
            // but rely on the server to send us an update via
            // websocket.
        }

        return workingCopyNew;
    }

    // remove subscription from cache item.  ix is the subscription
    // handle that was returned by get etc.
    function unsubscribe(path : string, ix : number) : void {
        unregisterSubscription(path, cache.get(path), ix);
    }

    function destroy() {
        ws.destroy();
        cache.destroy();
    }



    //////////////////////////////////////////////////////////////////////
    // private helper functions

    // Create item with empty content.  Subscriptions map is empty;
    // freshName is initialized to start counding at 0.
    function createEmptyItem(path : string) : ICacheItem {
        function freshNamer() : () => number {
            var x : number = 0;
            return () => { return x++; };
        }

        var item : ICacheItem = {
            pristine: undefined,
            subscriptions: {},
            freshName: freshNamer(),
        };

        cache.put(path, item);
        return item;
    }

    // Load pristine content into item.  Register web socket listener
    // callback.  (The callback checks if object is still needed on
    // every server update.  If so, it is kept up-to-date.  If not, it
    // is dropped from the cache.)
    //
    // Return pristine content.
    function initItem(item : ICacheItem, path : string) : (obj : Types.Content) => Types.Content {
        return (obj) => {
            item.pristine = obj;

            ws.subscribe(path, () => {
                if (Object.keys(item.subscriptions).length === 0) {
                    // if no subscriptions exist, drop item from cache.

                    ws.unsubscribe(path);
                    cache.remove(path);
                } else {
                    // if subscriptions exist, store newly fetched
                    // content in cache item and call all subscribed
                    // updateModel functions.  each call
                    // receives its own deep copy as argument.

                    adhHttp.get(path).then((obj) => {
                        item.pristine = obj;
                        for (var ix in item.subscriptions) {
                            item.subscriptions[ix](Util.deepcp(obj));
                        }
                    });
                }

                // FIXME: make sure there is no concurrency issue here: what
                // if the update callback is already queued, but then the item
                // is removed from cache?
            });

            return obj;
        };
    }

    function registerSubscription(item : ICacheItem, updateModel : (obj : Types.Content) => void) : number {
        var ix = item.freshName();
        item.subscriptions[ix] = updateModel;
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
        commit: commit,
        unsubscribe: unsubscribe,
        destroy: destroy,
    };
}



// TODO:
//
//   - http error handling
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
