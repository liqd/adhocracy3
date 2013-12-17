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


    // web sockets

    // FIXME: first draft, using a primitive global dictionary for
    // registering models interested in updates.  (i don't think this
    // is what we actually want to do once the application gets more
    // complex, but i want to find out how well it works anyway.  see
    // also angularjs github wiki, section 'best practice'.)

    // FIXME: make this part of module 'Adhocracy/Service/Http'?  Or
    // 'Adhocracy/Service/WS'?

    var subscriptions = {};

    function subscribe(path : string, model : {ref: any}, flushPath ?: boolean) : void {
        debugger;

        if (!(path in subscriptions) || flushPath)
            subscriptions[path] = [];
        subscriptions[path].push(model);
    }

    function unsubscribe(path : string, model : {ref: any}, strict ?: boolean) : void {
        debugger;

        function crash() : void {
            if (strict)
                throw 'unsubscribe web socket listener: no subscription for ' + [path, model] + '!'
        }

        if (path in subscriptions) {
            var ix = subscriptions[path].indexOf(model);
            if (ix) Util.reduceArray(subscriptions[path], ix, ix);
            else crash();
        } else {
            crash();
        }
    }

    function createWs(adhHttp : AdhHttp.IService) {
        var wsuri = 'ws://' + window.location.host + jsonPrefix + '?ws=node';
        var ws = new WebSocket(wsuri);

        ws.onmessage = function(event) {
            var path = event.data;
            console.log('web socket message: update on ' + path);
            debugger;

            if (path in subscriptions) {
                console.log('subscribers: ' + subscriptions[path]);

                adhHttp.get(path).then(function(d) {
                    for (var k in subscriptions[path]) {
                        subscriptions[path][k].ref = d;
                    }
                });
            } else {
                console.log('subscribers: []');
            }
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

        return ws;
    }

    function closeWs(ws) : void {
        console.log('closeWs');
        ws.close();
    }


    // controller

    app.controller('AdhDocumentTOC', function(adhHttp : AdhHttp.IService,
                                              $scope : any,  /* FIXME: better type here! */
                                              $rootScope : ng.IScope) {
        var ws = createWs(adhHttp);

        adhHttp.get(jsonPrefix).then(function(d) {
            var pool = d.data['P.IPool'];

            $scope.directory = [];

            // show paths only.  (not very interesting.)
            // $scope.directory = pool.elements.map(function(d) { return d.path });

            // show names of heads of dags under paths.  this yields a
            // directory in non-deterministic order.  which is ok; we want
            // to change order and filters dynamically anyway.
            //
            // FIXME: rewrite.  see showDetail below.
            // FIXME: use adhHttp.drill.
            pool.elements.map(function(ref) {
                adhHttp.get(ref.path).then(function(dag) {
                    var dagPS = dag.data['P.IDAG'];
                    if (dagPS.versions.length > 0) {
                        var dagPath = dag.path;
                        var headPath = dagPS.versions[0].path;
                        adhHttp.get(headPath).then(function(doc) {
                            var docPS = doc;
                            $scope.directory.push([headPath, docPS]);
                            // subscribe($scope.detail.path, $scope.detail, true);
                        });
                    } else {
                        $scope.directory.push(undefined);
                    }
                });
            });
        });

        // FIXME: the rest of this controller wants to be rewritten.
        // the idea should be that all the different $scope variables
        // are all contained in one object that is $watched by the
        // view and that we never have to call showDetail to begin
        // with.  (i think.)

        function clearDetail() {
            $scope.detail = {};
            $scope.detail_paragraphs = {ref: [], xpath: []};
            $scope.detail_mode = 'display';
        }

        clearDetail();
        this.showDetail = function(path) {
            clearDetail();

            adhHttp.get(path).then(function(data) {
                $scope.detail = { ref: data };
                adhHttp.drill(data, ['P.IDocument', ['paragraphs'], 'P.IParagraph'],
                              $scope.detail_paragraphs, true);

                // add web socket listener even in detail view,
                // because some other client may update it.  (no need
                // to watch entire nested structure because document
                // root will always be affacted of any changes there.)
                subscribe($scope.detail.path, $scope.detail, true);
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
            return '[' + ref.data['P.IDocument'].title + ']';
        };
    }]);


    // get going

    angular.bootstrap(document, ['NGAD']);

}
