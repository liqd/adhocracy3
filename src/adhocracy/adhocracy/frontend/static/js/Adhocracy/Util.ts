import Types = require('Adhocracy/Types');


// Array Remove - By John Resig (MIT Licensed)
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
    if (typeof(i) == 'object') {
        var o : Object;
        if (i == null)                o = null;
        else if (i instanceof Array)  o = new Array();
        else                          o = new Object();

        for (var x in i) o[x] = deepcp(i[x]);
        return o;
    } else {
        return i;
    }
}


// Compare two objects, and return a boolen that states whether they
// are equal.  (This is likely to be an approximation, but it should
// work at least for json objects.)
export function deepeq(a : any, b : any) : boolean {
    if (typeof a != typeof b)
        return false;

    if (typeof(a) == 'object') {
        if (a == null) return (b == null);

        for (var x in a) {
            if (!(x in b)) return false;
            if (!deepeq(a[x], b[x])) return false;
        }

        for (var x in b) {
            if (!(x in a)) return false;
        }
    }

    return true;
}