var app = angular.module('ATestMod', []);


app.controller('ATest', function(adhGet, $scope) {
    this.path = '/adhocracy';

    adhGet(this.path).then(function(d) {
        var pool = d.data['adhocracy.propertysheets.interfaces.IPool'];

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
                var dagPS = dag.data['adhocracy.propertysheets.interfaces.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhGet(headPath).then(function(doc) {
                        var docPS = doc.data['adhocracy.propertysheets.interfaces.IDocument'];
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
        adhGet(path).then(function(data) {
            $scope.detail = data;

            var paragraphRefs = data.data['adhocracy.propertysheets.interfaces.IDocument'].paragraphs;
            for (ix in paragraphRefs) {
                adhGet(paragraphRefs[ix].path).then((function(ix) {
                    return function(paragraph) {
                        $scope.detail_paragraphs[ix] = paragraph.data['adhocracy.propertysheets.interfaces.IParagraph'].text;
                    };
                })(ix));
            }
        });
    }

    this.qty = 7;
    this.cost = 8;
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
            return response.data;
        });
    }
});
