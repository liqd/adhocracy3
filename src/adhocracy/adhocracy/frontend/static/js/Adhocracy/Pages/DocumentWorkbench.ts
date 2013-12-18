/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require('angular');

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');
import AdhHttp = require('Adhocracy/Services/Http');
import AdhWS = require('Adhocracy/Services/WS');

var templatePath : string = '/static/templates';
var appPrefix : string = '/app';


export function run() {
    var app = angular.module('NGAD', []);


    // services

    app.factory('adhHttp', ['$http', AdhHttp.factory]);


    // controller

    app.controller('AdhDocumentTOC', function(adhHttp : AdhHttp.IService,
                                              $scope : any,  /* FIXME: derive a better type from ng.IScope */
                                              $rootScope : ng.IScope) {
        var ws = AdhWS.factory(adhHttp);

        adhHttp.get(AdhHttp.jsonPrefix).then(function(d) {
            $scope.pool = d;
            ws.subscribe(d.path, function(d) { $scope.pool = d; });

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
                        ws.subscribe(path, (dag) => fetchHead(ix, dag));
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
