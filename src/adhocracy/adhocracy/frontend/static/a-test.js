var app = angular.module('Adhocracy', []);


app.controller('AdhDocumentTOC', function(adhHttp, $scope) {
    this.path = '/adhocracy';

    adhHttp.get(this.path, ['P.Pool']).then(function(d) {
        var pool = d.data['P.IPool'];

        $scope.directory = [];

        // show paths only.
        // $scope.directory = pool.elements.map(function(d) { return d.path });

        // show names of heads of dags under paths.  this yields a
        // directory in non-deterministic order.  which is ok; we want
        // to change order and filters dynamically anyway.
        //
        // FIXME: write a function that follows references
        // transparently through the data model.  (it takes an array
        // of field names, and follows these fields names down into an
        // object.  each time it hits a reference, the reference is
        // replaced by the referenced object before the path is
        // followed further.)
        pool.elements.map(function(ref) {
            adhHttp.get(ref.path).then(function(dag) {
                var dagPS = dag.data['P.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhHttp.get(headPath).then(function(doc) {
                        var docPS = doc.data['P.IDocument'];
                        $scope.directory.push([headPath, docPS.title]);
                    });
                } else {
                    $scope.directory.push(undefined);
                }
            });
        });
    });

    $scope.detail = {};
    $scope.detail_paragraphs = [];

    this.showDetail = function(path) {
        $scope.detail = {};
        $scope.detail_paragraphs = [];  // for testing: [{text: 'wef'}, {text: 'foqf'}]

        adhHttp.get(path).then(function(data) {
            $scope.detail = data;
            adhHttp.drill(data, ['P.IDocument', ['paragraphs'], 'P.IParagraph'],
                          $scope.detail_paragraphs, true);

            @@@     //      @@@ problem: drill works fine up to the
                    //      point where something should be written to
                    //      target.  i don't understand the calling
                    //      physics of js functions...  perhaps wrap
                    //      it in another array, and write into one
                    //      element?  -mf

        });
    }

    this.qty = 7;
    this.cost = 8;
});


app.directive('adhDocumentWorkbench', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/P/IDocument/Workbench.html',
    }
});


app.directive('adhDocumentDetail', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/templates/P/IDocument/ViewDetail.html',
    }
});



// filters

app.filter('fDirectoryEntry', [ function() {
    // (dummy filter to show how this works.  originally, i wanted to
    // pull more data asynchronously here, but i'm not sure this is
    // supposed to work.)
    return function(ref) {
        return '[' + ref + ']';
    };
}]);



// services

app.factory('adhHttp', function($http) {
    var adhHttp = {
        get: function(path) {
            return $http.get(path).then(function(response) {
                if (response.status != 200) {
                    console.log(response);
                    throw ('adhHttp.get: http error ' + response.status.toString() + ' on path ' + path);
                }
                return importContent(response.data);
            });
        },

        drill: function(data, xpath, target, ordered) {
            function resolveReference() {
                if ('path' in data) {
                    adhHttp.get(data['path']).then(function(resource) {
                        adhHttp.drill(resource, xpath, target, ordered);
                    });
                } else {
                    console.log(data);
                    throw 'adhHttp.drill: not a resource and not a reference.';
                }
            }

            if ('content_type' in data) {
                if ('data' in data) {
                    adhHttp.drill(data['data'], xpath, target, ordered);
                    return;
                } else {
                    resolveReference();
                    return;
                }
            } else {
                if (xpath.length == 0) {
                    target = data;
                    return;
                }
                var step = xpath.shift();
                if (typeof step == 'string' || typeof step == 'number') {
                    adhHttp.drill(data[step], xpath, target, ordered);
                    return;
                }
                if (step instanceof Array) {
                    if (step.length != 1 || !(typeof(step[0]) == 'string' || typeof(step[0]) == 'number')) {
                        // FIXME: what about "[[[step]]]"?
                        console.log(step);
                        throw 'internal';
                    }
                    step = step[0];

                    if (!(data[step] instanceof Array)) {
                        console.log(data);
                        console.log(step);
                        throw 'internal';
                    }
                    elements = data[step];

                    // if target is not an array, make it one.
                    if (!(target instanceof Array)) {
                        target = [];
                    }

                    if (!ordered) {
                        throw 'not implemented.';
                    }

                    // loop over step, and call drill recursively on
                    // each element, together with the corresponding
                    // element of target.
                    for (ix in elements) {
                        adhHttp.drill(elements[ix], xpath, target[ix], ordered);
                    }
                    return;
                }
            }
        },
    };

    return adhHttp;
});



// plumbing

var importContent = translateContent(shortenType);
var exportContent = translateContent(unshortenType);

var contentTypeNameSpaces = {
    'adhocracy.contents.interfaces': 'C'
}

var propertyTypeNameSpaces = {
    'adhocracy.propertysheets.interfaces': 'P'
}

function shortenType(nameSpaces) {
    return function(s) {
        var t = s;
        for (k in nameSpaces) {
            t = t.replace(new RegExp('^' + k + '(\\.[^\\.]+)$'), nameSpaces[k] + '$1');
        }
        return t;
    }
}

function unshortenType(nameSpaces) {
    return function(s) {
        var t = s;
        for (k in nameSpaces) {
            t = t.replace(new RegExp('^' + nameSpaces[k] + '(\\.[^\\.]+)$'), k + '$1');
        }
        return t;
    }
}

function translateContent(translateType) {
    return function(inobj) {
        var outobj = {
            content_type: translateType(contentTypeNameSpaces)(inobj.content_type),
            path: inobj.path,
            data: {},
        }

        for (i in inobj.data) {
            var i_local = translateType(propertyTypeNameSpaces)(i);
            outobj.data[i_local] =
                changeContentTypeRecursively(inobj.data[i],
                                             translateType(contentTypeNameSpaces));
        }

        return outobj;
    }
}

function changeContentTypeRecursively(obj, f) {
    var t = Object.prototype.toString.call(obj);

    switch(t) {
    case '[object Object]':
        var newobj = {};
        for (var k in obj) {
            if (k == 'content_type') {
                newobj[k] = f(obj[k]);
            } else {
                newobj[k] = changeContentTypeRecursively(obj[k], f);
            }
        }
        return newobj;

    case '[object Array]':
        return obj.map(function(el) { return changeContentTypeRecursively(el, f); });

    default:
        return obj;
    }
}

function deepcp(i) {
    if (typeof(i) == 'object') {
        if (typeof(i.length) != 'undefined')
            var o = new Array();
        else
            var o = new Object();
        for (var x in i)
            o[x] = deepcp(i[x]);
        return o;
    } else {
        return i;
    }
}
