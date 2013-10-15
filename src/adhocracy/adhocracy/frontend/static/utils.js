
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
function collectChangedNodes(repo, obj) {
    console.log(obj);
    throw 'not yet implemented.';

/*


stand der diskussion, Mon Sep 23 17:32:18 CEST 2013, niko, sönke, matthias

 - currently there is no reliable information about the supergraph
   structure on the client side.  urls cannot be reliably recognised
   as edges, and conceivably some sub-trees in a json object already
   constitute separate nodes.  it is under discussion whether this
   lack of information is a vital problem.  but we probably want to at
   least know which are the outgoing essence refs.

 - xpath-idea: if the save function gets an obj and a tree structure
   to traverse the obj, then the repo (which is essentially an
   optimization of more ajax GETs) can be used to retrieve the
   relevant pieces of the supergraph, test them for changes, and post
   those that have changed back to the server.

 - one important feature: if a paragraph is changed, the proposal
   needs to know.  the gui developer may want to place the only save
   button next to the proposal title, together with a count of the
   changed paragraphs.



    console.log(obj.meta.path);
    console.log(repo[obj.meta.path]);

    var orig = repo[obj.meta.path];

    if (obj != orig) {
	console.log('post');
    };
*/

};

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

var showjs = function(json) {
    return JSON.stringify(json, null, 2)
};

function deepCopy(obj) {
    return jQuery.extend(true, {}, obj);
};
