/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require('angular');

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');
import AdhHttp = require('Adhocracy/Services/Http');

var templatePath : string = '/static/templates';
var jsonPrefix : string = '/adhocracy';
var appPrefix : string = '/app';


export function run() {
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



    // callbacks for websocket signals are a good idea.  unravelling
    // should also work somehow: if a callback receives an object that
    // contains references, it keeps calling adhHttp.get more, with
    // more callbacks, that update the referenced models.

    // FIXME: tear things down properly (unsubscribe, closeWs)



    function subscribe(path : string, update : (model: any) => void) : void {
        subscriptions[path] = update;
    }

    function unsubscribe(path : string, strict ?: boolean) : void {
        if (path in subscriptions)
            delete subscriptions[path];
        else if (strict)
            throw 'unsubscribe web socket listener: no subscription for ' + path + '!'
    }

    function createWs(adhHttp : AdhHttp.IService) {
        var wsuri = 'ws://' + window.location.host + jsonPrefix + '?ws=all';
        console.log('createWs: ' + wsuri);
        var ws = new WebSocket(wsuri);

        ws.onmessage = function(event) {
            var path = event.data;
            console.log('web socket message: update on ' + path);

            if (path in subscriptions) {
                console.log('subscriber: ' + subscriptions[path]);
                adhHttp.get(path).then(subscriptions[path]);
            } else {
                console.log('(no subscriber)');
            }
        };

        // some console info to keep track of things happening:
        ws.onerror = function(event) {
            console.log('ws.onerror: ' + event.toString());
        };
        ws.onopen = function() {
            console.log('ws.onopen');
        };
        ws.onclose = function() {
            console.log('ws.onclose');
        };

        return ws;
    }

    function closeWs(ws) : void {
        console.log('closeWs');
        ws.close();
    }


    // controller

    app.controller('AdhDocumentTOC', function(adhHttp : AdhHttp.IService,
                                              $scope : any,  /* FIXME: derive a better type from ng.IScope */
                                              $rootScope : ng.IScope) {
        var ws = createWs(adhHttp);

        adhHttp.get(jsonPrefix).then(function(d) {
            $scope.pool = d;
            subscribe(d.path, function(d) { $scope.pool = d; });

            $scope.poolEntries = [];

            function fetchHead(ix : number, dag : Types.Content) : void {
                var dagPS = dag.data['P.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhHttp.get(headPath).then(function(doc) {
                        var docPS = doc;
                        $scope.poolEntries[ix] = [headPath, docPS];
                    });
                } else {
                    $scope.poolEntries[ix] = undefined;
                }
            }

            function init() {
                var els : Types.Content[] = d.data['P.IPool'].elements;
                for (var ix in els) {
                    (function(ix : number) {
                        var path : string = els[ix].path;
                        subscribe(path, (dag) => fetchHead(ix, dag));
                        adhHttp.get(path).then((dag) => fetchHead(ix, dag));
                    })(ix);
                }
            }

            init();
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

                // add web socket listener even in detail view,
                // because some other client may update it.  (no need
                // to watch entire nested structure because document
                // root will always be affacted of any changes there.)
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
            var oldVersionPath : string = $scope.detail_old.path;
            if (typeof oldVersionPath == 'undefined') {
                console.log($scope.detail_old);
                throw 'showDetailSave: detail_old.'
            }
            adhHttp.postNewVersion(oldVersionPath, $scope.detail, function() {
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
