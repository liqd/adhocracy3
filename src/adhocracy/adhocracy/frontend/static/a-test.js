var app = angular.module('Adhocracy', []);


app.controller('AdhDocumentTOC', function(adhGet, $scope) {
    this.path = '/adhocracy';

    adhGet(this.path).then(function(d) {
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
            adhGet(ref.path).then(function(dag) {
                var dagPS = dag.data['P.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhGet(headPath).then(function(doc) {
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
        $scope.detail_paragraphs = [];

        adhGet(path).then(function(data) {
            $scope.detail = data;

            var paragraphRefs = data.data['P.IDocument'].paragraphs;
            for (ix in paragraphRefs) {
                adhGet(paragraphRefs[ix].path).then((function(ix) {
                    return function(paragraph) {
                        $scope.detail_paragraphs[ix] = paragraph.data['P.IParagraph'].text;
                    };
                })(ix));
            }
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

app.factory('adhGet', function($http) {
    return function(path) {
        return $http.get(path).then(function(response) {
            if (response.status != 200) {
                console.log(response);
                throw ('adhGet: http error ' + response.status.toString() + ' on path ' + path);
            }
            return importContent(response.data);
        });
    }
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
