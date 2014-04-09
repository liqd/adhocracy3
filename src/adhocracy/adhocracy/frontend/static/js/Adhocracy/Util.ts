import Types = require("Adhocracy/Types");


// cut ranges out of an array - original by John Resig (MIT Licensed)
export function cutArray(a : any[], from : number, to ?: number) : any[] {
    var rest = a.slice((to || from) + 1 || a.length);
    a.length = from < 0 ? a.length + from : from;
    a.push.apply(a, rest);
    return a;
};

export function isInfixOf(needle : any, hay : any[]) : boolean {
    return hay.indexOf(needle) !== -1;
};

export function parentPath(url : string) : string {
    return url.substring(0, url.lastIndexOf("/"));
};


// Do a deep copy on any javascript object.  The resuling object does
// not share sub-structures as the original.  (I think instances of
// classes other than Object, Array are not treated properly either.)
export function deepcp(i) {
    if (typeof(i) === "object") {
        var o : Object;
        if (i === null) {
            o = null;
        } else if (i instanceof Array)  {
            o = new Array();
        } else {
            o = new Object();
        }

        for (var x in i) { o[x] = deepcp(i[x]); }
        return o;
    } else {
        return i;
    }
}


// Do a deep copy of a javascript source object into a target object.
// References to the target object are not severed; rather, all fields
// in the target object are deleted, and all fields in the source
// object are copied using deepcp().  Crashes if target is not an
// object.
export function deepoverwrite(source, target) {
    var k;
    try {
        for (k in target) {
            delete target[k];
        }
        for (k in source) {
            target[k] = deepcp(source[k]);
        }
    } catch (e) {
        throw ("Util.deepoverwrite: " + [source, target, e]);
    }
}


// Compare two objects, and return a boolen that states whether they
// are equal.  (This is likely to be an approximation, but it should
// work at least for json objects.)
export function deepeq(a : any, b : any) : boolean {
    if (typeof a !== typeof b) {
        return false;
    }

    if (typeof(a) === "object") {
        if (a === null) {
            return (b === null);
        }

        for (var x in a) {
            if (!(x in b))           { return false; }
            if (!deepeq(a[x], b[x])) { return false; }
        }

        for (var y in b) {
            if (!(y in a)) { return false; }
        }
    }

    return a === b;
}


// sugar for angular
export function mkPromise($q : ng.IQService, obj : any) : ng.IPromise<any> {
    var deferred = $q.defer();
    deferred.resolve();
    return deferred.promise.then(() => { return obj; });
}

export function normalizeName(name: string) : string {
    return name.toLowerCase().replace(/\ /g, "_");
}


//FIXME: backend should have LAST
export function newestVersion(versions: string[]) {
    return _.max(versions, (version_path) => parseInt(version_path.match(/\d*$/)[0], 10));
}