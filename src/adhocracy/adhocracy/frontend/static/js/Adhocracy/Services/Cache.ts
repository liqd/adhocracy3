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
//   - store on disk
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
var cacheSizeInObjects = 100;

export interface IService {
    subscribe : (path : string, update : (model: any) => void) => ng.IPromise<Types.Content>;
    unsubscribe : (path : string, strict ?: boolean) => void;
    destroy: () => void;
}

export function factory(adhHttp        : AdhHttp.IService,
                        adhWS          : AdhWS.IService,
                        $q             : ng.IQService,
                        $cacheFactory  : ng.ICacheFactoryService) : IService
{
    var cache = $cacheFactory('1', { capacity: cacheSizeInObjects });
    var ws = AdhWS.factory(adhHttp);

    // lookup object in cache.  in case of miss, retrieve and add it.
    // register update callback on its path and return a promise of the object.
    function subscribe(path : string, update : (model: any) => void) : ng.IPromise<Types.Content> {
        var model = cache.get(path);
        if (typeof model != 'undefined') {
            return $q.defer().promise.then(function() { return model; });
        } else {
            adhHttp.get(path).then((model : Types.Content) : Types.Content => {
                cache.put(path, model);
                ws.subscribe(path, (model : Types.Content) : void => {
                    cache.put(path, model);
                    update(model);
                });
                return model;
            });
        }
    }

    function unsubscribe(path : string) : void {
        return;
    }

    function destroy() {
        ws.destroy();
        cache.destroy();
    }

    return {
        subscribe: subscribe,
        unsubscribe: unsubscribe,
        destroy: destroy,
    };
}



// TODO:

//   - implement trivial unsubscribe

//   - leave object in cache and web socket open if it is unsubscribed
//     from app.  web socket update notifcations change meaning: if
//     subscribed from app, update; if not, drop from cache.

//   - maintain both a working copy copy and a pristine copy of server state
//   - get paragraphs working like documents work already

//   - diff working copy and pristine copy
//   - commit working copy of one object
//   - batch commit of a sequence of objects
//   - store on disk
//   - store commits indefinitely in case server is unavailable and sync after offline periods
