/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import AdhHttp = require('Adhocracy/Services/Http');
import AdhWS = require('Adhocracy/Services/WS');


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
    get          : (path : string, update : (model: any) => void) => void;
    commit       : (path : string)                                => void;
    reset        : (path : string)                                => void;
    subscribe    : (path : string, update : (model: any) => void) => void;
    unsubscribe  : (path : string, strict ?: boolean)             => void;
    destroy      : ()                                             => void;
}

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService
{
    var cache : ng.ICacheObject = $cacheFactory('1', { capacity: cacheSizeInObjects });
    var ws = AdhWS.factory(adhHttp);

    // lookup object in cache can call callback once immediately on
    // arrival of the object.
    //
    // in case of cache miss, retrieve and add it.  register an update
    // callback with its path that removes it from the cache if the
    // server sends an expiration notification.
    function get(path : string, update : (model: any) => void) : void {

        var model = cache.get(path);

        if (typeof model !== 'undefined') {
            console.log('cache hit!');
            writePath(cache, path, model);
            update(model);
        } else {
            console.log('cache miss!');
            adhHttp.get(path).then((model : Types.Content) : void => {
                writePath(cache, path, model);
                ws.subscribe(path, (model) => unsubscribe(path));
                update(model);
            });
        }
    }

    // FIXME: document!
    function commit(path : string) : void {
        var obj = cache.get(path);

        // if path is invalid, crash.
        if (typeof obj === 'undefined')
            throw "unknown path: " + path;

        // if working copy is unchanged, do nothing.
        if (obj.pristine === obj.working)
            return;

        // otherwise, post working copy and overwrite pristine with
        // new version from server.  (must be from server, since
        // server changes things like version successor and
        // predecessor edges.)
        adhHttp.postNewVersion(path, obj.working, (obj) => {
            obj.pristine = obj;
            obj.working = Util.deepcp(obj);
        });

        // notify application of the update.

        // FIXME: not implemented.

    }

    // FIXME: document!
    function reset(path : string) : void {
        resetPath(cache, path);
    }

    // lookup object in cache and call callback once immediately and
    // once on every update from the server, until unsubscribe is
    // called on this path.
    //
    // in case of miss, retrieve and add it.  register update callback
    // on its path.  the callback is called once now and then every
    // time the object is updated in cache, until unsubscribe is
    // called on this path.
    function subscribe(path : string, update : (model: any) => void) : void {

        var model = cache.get(path);

        if (typeof model !== 'undefined') {
            console.log('cache hit!');
            writePath(cache, path, model);
            update(model);

            // if we had to return a promise from this function, and
            // had to construct one from the promised value, this is
            // what we could do:
            //
            //   return $q.defer().promise.then(function() { return model; });
            //
            // (just leaving this in because it's so pretty :-)
        } else {
            console.log('cache miss!');
            adhHttp.get(path).then((model : Types.Content) : void => {
                writePath(cache, path, model);
                ws.subscribe(path, update);
                update(model);
            });
        }
    }

    function unsubscribe(path : string) : void {
        ws.unsubscribe(path);
        cache.remove(path);

        // FIXME: make sure there is no concurrency issue here: what
        // if the update callback is already queued, but then the
        // model is removed from cache?  won't that trigger a reload,
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



// overwrite pristine copy.  this must only be done with content data
// retrieved from the server.  throw an exception if get yields
// nothing.
function updatePristine(cache : ng.ICacheObject, path : string, model : Types.Content) : void {
    var obj = cache.get(path);

    if (typeof obj === 'undefined')
        throw "nothing found at " + path;
    else
        obj.pristine = model;
}

// overwrite working copy with pristine.  throw an exception if get
// yields nothing.
function resetPath(cache : ng.ICacheObject, path : string) : void {
    var obj = cache.get(path);

    if (typeof obj === 'undefined')
        throw "nothing found at " + path;
    else
        obj.working = Util.deepcp(obj.pristine);
}

// overwrite woth pristine and working copy with arg.  pristine is a
// reference to the arg, working copy is a deep copy.
function writePath(cache : ng.ICacheObject, path : string, model : Types.Content) : void {
    cache.put(path, { pristine: model, working: Util.deepcp(model) });
}

// check if object differs between pristine and working copy.  throws
// an exception if get yields nothing.
function workingCopyChanged(cache : ng.ICacheObject, path : string) : boolean {
    var old = cache.get(path);
    if (typeof old == 'undefined')
        throw 'nothing found at ' + path;
    else
        return old.working != old.pristine;
}



// TODO:
//
//   - commit working copy of one object
//   - think about concurrent sanity of commit, reset (what if pristine changes while user changes working copy?)
//   - batch commit of a sequence of objects
//
//   - leave object in cache and web socket open if it is unsubscribed
//     from app.  web socket update notifcations change meaning: if
//     subscribed from app, update; if not, drop from cache.
//
//   - store on disk
//   - store commits indefinitely in case server is unavailable and sync after offline periods
