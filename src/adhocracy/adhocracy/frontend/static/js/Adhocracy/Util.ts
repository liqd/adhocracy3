import Types = require('Adhocracy/Types');


export function isInfixOf(needle, hay) : boolean {
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
        if (i instanceof Array)  o = new Array();
        else                     o = new Object();
        for (var x in i)         o[x] = deepcp(i[x]);
        return o;
    } else {
        return i;
    }
}
