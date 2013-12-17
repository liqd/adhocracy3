/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');
import AdhHttp = require('Adhocracy/Services/Http');

declare module 'angular' {
    // FIXME: complete this, fill in more concise types, and write a pull request for definitely typed.
    export var module: any;
    export var bootstrap: any;
}

import angular = require('angular');

var templatePath : string = '/static/templates';
var jsonPrefix : string = '/adhocracy';
var appPrefix : string = '/app';


export function run() {
    console.log('DocumentWorkbench.run()');
    var app = angular.module('NGAD', []);


    // services

    app.factory('adhHttp', ['$http', AdhHttp.factory]);


    // controller

    app.controller('AdhDocumentTOC', function(adhHttp, $scope) {
        adhHttp.get(jsonPrefix, ['P.Pool']).then(function(d) {
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
            $scope.detail_old = Util.deepcp($scope.detail);
            $scope.detail_mode = 'edit';
        }

        this.showDetailReset = function() {
            $scope.detail = Util.deepcp($scope.detail_old);
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
            templateUrl: templatePath + '/P/IDocument/Workbench.html',
        }
    });


    app.directive('adhDocumentDetail', function() {
        return {
            restrict: 'E',
            templateUrl: templatePath + '/P/IDocument/ViewDetail.html',
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


    // get going

    angular.bootstrap(document, ['NGAD']);

}



// web sockets

// FIXME: make this part of module 'Adhocracy/Service/Http'?  Or 'Adhocracy/Service/WS'?

var wsdict = {};

// Create a web socket and connect it to a dom element for online
// updates.  If an old web socket was registered, close and delete it.
// Do *not* render the dom element once initially.  Do *not* push new
// state to history api stack (this is only desired for *one* dom
// element per page).
//
// FIXME: each time a render is triggered, the queue should be flushed
// and compressed first.  as it is, if a proposal pool is growing by
// three proposals before a client looks at the web socket queue
// again, the client will render the latest version three times rather
// than once.
export function updateWs(sizzle : string, path : string, viewName ?: string) : void {
    console.log('updateWs: ' + sizzle, path, viewName);

    if (sizzle in wsdict) {
        if (wsdict[sizzle].path == path) {
            wsdict[sizzle].viewName = viewName;
            return;
        } else {
            closeWs(sizzle);
            makeNew();
            return;
        }
    } else {
        makeNew();
        return;
    }

    function makeNew() {
        var wsuri = 'ws://' + window.location.host + path + '?ws=node';
        var ws = new WebSocket(wsuri);

        wsdict[sizzle] = {
            path: path,
            viewName: viewName,
            ws: ws,
        }

        ws.onmessage = function(event) {
            // var path = event.data;
            // (we don't need to do this; every path gets its own web socket for now.)

            console.log('ws.onmessage: updating '  + wsdict[sizzle].path
                        + ' with view '            + wsdict[sizzle].viewName
                        + ' on dom node:\n'        + sizzle);

            throw "not implemented";

            // $(sizzle).render(wsdict[sizzle].path, wsdict[sizzle].viewName);
        };

        // some console info to keep track of things happening:
        ws.onerror = function(event) {
            console.log('ws.onerror: ' + event.toString());
        };
        ws.onopen = function() {
            console.log('[ws.onopen]');
        };
        ws.onclose = function() {
            console.log('[ws.onclose]');
        };
    }
}

export function closeWs(sizzle : string) {
    console.log('closeWs: ' + sizzle);

    if (sizzle in wsdict) {
        wsdict[sizzle].ws.close();
        delete wsdict[sizzle];
    }
}
