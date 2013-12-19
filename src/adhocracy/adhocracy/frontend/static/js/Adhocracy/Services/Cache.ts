/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/jquery/jquery.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import AdhHttp = require('Adhocracy/Services/Http');
import AdhWS = require('Adhocracy/Services/WS');


// cache

// this module provides an api that
//
//   - stores objects locally (in memory and on disk);
//   - tracks expire notifications via web socket and (after offline periods) via sync;
//   - maintains both a local, modifiable copy and a pristine server copy;
//   - provides diff, commit, and batch commit functionality;
//   - can store commits indefinitely in case server is unavailable.
//
// lib options for caching:
//
//  1. the angular-builtin $cacheFactory (leaves all the
//     adhocracy-specific stuff to me without trying to guess how it's
//     done.  it can also very very implicitly with $http, which i
//     don't think is a good idea.)
//
//  2. github.com/jmdobry/angular-cache (about expiration time
//     guessing, but i want to be explicit about what expires and what
//     lives.  also supports local storage.  perhaps even better than
//     1.?)
//
//  3. http://gregpike.net/demos/angular-local-storage/demo/demo.html
//     (writes to disk, which is also interesting.)
