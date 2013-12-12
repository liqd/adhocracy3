var app = angular.module('ATestMod', []);


app.controller('ATest', function(adhGet, $scope) {
    this.path = '/adhocracy';
    $scope.directory;

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
        // transparently through the data model.
        pool.elements.map(function(ref) {
            adhGet(ref.path).then(function(d) {
                var dag = d.data['adhocracy.propertysheets.interfaces.IDAG'];
                if (dag.versions.length > 0) {
                    var headPath = dag.versions[0].path;
                    adhGet(headPath).then(function(d) {
                        var doc = d.data['adhocracy.propertysheets.interfaces.IDocument'];
                        $scope.directory.push(doc.title);
                    });
                } else {
                    $scope.directory.push('(empty)');
                }
            });
        });
    });

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
