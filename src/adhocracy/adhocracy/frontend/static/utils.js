
// global object to store our functionality
ad = {}

// repo: record all ajax responses in a dictionary mapping paths to
// json objects.  the recording happens in the transformer; the
// recorded information is used when saving changes on the server.
ad.repo = {};

// lookup path in the meta data of obj.  lookup obj in ad.repo.  if
// obj has changed, add it to output list.  collect all attributes
// recursively that occur anywhere inside obj, lookup strings in
// ad.repo, and recurse wherever lookup yields a hit.  (this is not a
// very clean approach.  urls should have their own type.  strings
// that are not meant to be urls, but happen to are identical to a key
// in ad.repo should not yield hits.  but we haven't found a better
// way to do this yet.)
function collectChangedNodes(obj) {
    // FIXME: nyi

    return [];
}


function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

function deepCopy(obj) {
    return jQuery.extend(true, {}, obj);
};
