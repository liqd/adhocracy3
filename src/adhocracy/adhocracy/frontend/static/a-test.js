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

    function clearDetail() {
        $scope.detail = {};
        $scope.detail_paragraphs = {ref: [], xpath: []};
        $scope.detail_mode = 'display';
    }

    clearDetail();
    this.showDetail = function(path) {
        clearDetail();

        adhHttp.get(path).then(function(data) {
            $scope.detail = data;
            adhHttp.drill(data, ['P.IDocument', ['paragraphs'], 'P.IParagraph'],
                          $scope.detail_paragraphs, true);
        });
    }

    this.showDetailEdit = function() {
        $scope.detail_old = deepcp($scope.detail);
        $scope.detail_mode = 'edit';
    }

    this.showDetailReset = function() {
        $scope.detail_mode = 'display';
    }

    this.showDetailSave = function() {
        adhHttp.postNewVersion($scope.detail_old.path, $scope.detail, function() {
            $scope.detail_mode = 'display';
        });
    }
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

// import 'Adhocracy/Services/AdhHttp'
app.factory('adhHttp', AdhHttp.adhHttpFactory);
