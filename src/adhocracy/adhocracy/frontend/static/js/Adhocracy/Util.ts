/// <reference path="../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

/**
 * cut ranges out of an array - original by John Resig (MIT Licensed)
 */
export function cutArray(a : any[], from : number, to ?: number) : any[] {
    "use strict";
    var rest = a.slice((to || from) + 1 || a.length);
    a.length = from < 0 ? a.length + from : from;
    a.push.apply(a, rest);
    return a;
};

export function isInfixOf(needle : any, hay : any[]) : boolean {
    "use strict";
    return hay.indexOf(needle) !== -1;
};

/**
 * isArrayMember could be inlined, but is not for two reasons: (1)
 * even though js developers are used to it, the inlined idiom is just
 * weird; (2) the test suite documents what can and cannot be done
 * with it.
 */
export function isArrayMember(member : any, array : any[]) : boolean {
    "use strict";
    return array.indexOf(member) > -1;
}

export function parentPath(url : string) : string {
    "use strict";

    return url.substring(0, url.lastIndexOf("/"));
};


/**
 * Do a deep copy on any javascript object.  The resuling object does
 * not share sub-structures as the original.  (I think instances of
 * classes other than Object, Array are not treated properly either.)
 */
export function deepcp(i) {
    "use strict";

    if (typeof(i) === "object") {
        var o : Object;
        if (i === null) {
            o = null;
        } else if (i instanceof Array)  {
            o = new Array();
        } else {
            o = new Object();
        }

        for (var x in i) {
            if (i.hasOwnProperty(x)) {
                o[x] = deepcp(i[x]);
            }
        }
        return o;
    } else {
        return i;
    }
}


/**
 * Do a deep copy of a javascript source object into a target object.
 * References to the target object are not severed; rather, all fields
 * in the target object are deleted, and all fields in the source
 * object are copied using deepcp().  Crashes if target is not an
 * object.
 */
export function deepoverwrite(source, target) {
    "use strict";

    var k;
    try {
        for (k in target) {
            if (target.hasOwnProperty(k)) {
                delete target[k];
            }
        }
        for (k in source) {
            if (source.hasOwnProperty(k)) {
                target[k] = deepcp(source[k]);
            }
        }
    } catch (e) {
        throw ("Util.deepoverwrite: " + [source, target, e]);
    }
}


/**
 * Compare two objects, and return a boolen that states whether they
 * are equal.  (This is likely to be an approximation, but it should
 * work at least for json objects.)
 */
export function deepeq(a : any, b : any) : boolean {
    "use strict";

    if (typeof a !== typeof b) {
        return false;
    }

    if (typeof(a) === "object") {
        if (a === null) {
            return (b === null);
        }

        for (var x in a) {
            if (a.hasOwnProperty(x)) {
                if (!(x in b)) {
                    return false;
                }
                if (!deepeq(a[x], b[x])) {
                    return false;
                }
            }
        }

        for (var y in b) {
            if (b.hasOwnProperty(y)) {
                if (!(y in a)) {
                    return false;
                }
            }
        }
        return true;
    } else {
        return a === b;
    }
}


// sugar for angular
export function mkPromise($q : ng.IQService, obj : any) : ng.IPromise<any> {
    "use strict";

    var deferred = $q.defer();
    deferred.resolve();
    return deferred.promise.then(() => obj);
}

export function normalizeName(name: string) : string {
    "use strict";

    return name.toLowerCase().replace(/\ /g, "_");
}

/**
 * Take a maximum delay time, an array of arguments and a function.
 * Generate random delays (in ms) for each and calls the function
 * asynchronously (out of order) on each element of the array.  Ignore
 * return values of f.
 *
 * Example:
 *
 * | trickle($timeout, 5000, paths, (path) => $scope.messages.push({ "event": "modified", "resource": path }));
 */
export var trickle = <T>($timeout: ng.ITimeoutService, maxdelay: number, xs: T[], f: (T) => void): void => {
    xs.map((x) => $timeout(() => f(x), Math.random() * maxdelay, true));
};
