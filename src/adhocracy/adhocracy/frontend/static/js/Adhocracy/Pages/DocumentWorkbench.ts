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
                    adhHttp.get(headPath).then(function(headContent) {
                        var paragraphs = [];
                        fetchDocumentDetails(headContent,
                                             (ix, paragraph) => { paragraphs[ix] = paragraph });

                        // FIXME: use extend for the following.

                        if (ix in $scope.poolEntries) {
                            $scope.poolEntries[ix].path = headPath;
                            $scope.poolEntries[ix].content = headContent;
                            $scope.poolEntries[ix].details = paragraphs;
                        } else {
                            $scope.poolEntries[ix] = {
                                path: headPath,
                                content: headContent,
                                mode: 'list',
                                details: paragraphs,
                            }
                        }
                    });
                } else {
                    $scope.poolEntries[ix] = undefined;
                }
            }

            function fetchDocumentDetails(document : Types.Content,
                                          update : (ix : number, paragraph : Types.Content) => void) : void {
                var refs : Types.Reference[] = document['data']['P.IDocument']['paragraphs'];
                var ix : string;  // must be type 'string' or 'any'
                for (ix in refs) {
                    (function(ix) {
                        var path : string = refs[ix]['path'];
                        adhHttp.get(path).then((paragraph) => update(ix, paragraph));
                    })(ix);
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


        this.showTitle = function(entry) {
            entry.mode = 'list';
        }

        this.showDetailEdit = function(entry) {
            entry.previously = Util.deepcp(entry);
            entry.mode = 'edit';
        }

        this.showDetailReset = function(entry) {
            if ('previously' in entry)
                delete entry.previously;
            entry.mode = 'display';
        }

        this.showDetailSave = function(entry) {
            var oldVersionPath : string = entry.previously.path;
            if (typeof oldVersionPath == 'undefined') {
                console.log(entry.previously);
                throw 'showDetailSave: no previous path!'
            }
            adhHttp.postNewVersion(oldVersionPath, entry.content, function() {});

            // FIXME: post updates on paragraphs separately somehow.

            this.showDetailReset(entry);
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
