/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require('angular');

import Types = require('Adhocracy/Types');
import Util = require('Adhocracy/Util');
import Css = require('Adhocracy/Css');
import AdhHttp = require('Adhocracy/Services/Http');
import AdhWS = require('Adhocracy/Services/WS');
import AdhCache = require('Adhocracy/Services/Cache');

var templatePath : string = '/static/templates';
var appPrefix : string = '/app';


// the model object that contains the contents of the resource, the
// view mode (and possibly more stuff in the final implementation).
interface IDocument {
    viewmode    : string;
    content     : Types.Content;
    path        : string;
    previously ?: IDocument;
}

interface IDocumentTOCScope extends ng.IScope {
    pool : Types.Content;
    poolEntries : IDocument[];
    doc : IDocument;  // (iterates over document list with ng-repeat)
}

interface IDocumentDetailScope extends IDocumentTOCScope {
    viewmode : string;
}

interface IParagraphDetailScope extends IDocumentDetailScope {
    parref      : Types.Reference;
    parcontent  : Types.Content;
}

// FIXME: consider using isolated scopes in order to avoid inheriting
// model data.


export function run() {
    var app = angular.module('NGAD', []);


    // services

    app.factory('adhHttp',   ['$http',                                    AdhHttp.factory]);
    app.factory('adhWS',     ['adhHttp',                                  AdhWS.factory]);
    app.factory('adhCache',  ['adhHttp', 'adhWS', '$q', '$cacheFactory',  AdhCache.factory]);


    // filters

    app.filter('viewFilterList', [ function() {
        return function(obj : Types.Content) : string {
            return obj.data['P.IDocument'].title;
        };
    }]);


    // controllers

    app.controller('AdhDocumentTOC', function(adhHttp     : AdhHttp.IService,  // FIXME: don't use http, just use cache.
                                              adhCache    : AdhCache.IService,
                                              $scope      : IDocumentTOCScope,
                                              $rootScope  : ng.IScope
                                             ) {

        console.log('TOC: ' + $scope.$id);

        adhCache.subscribe(AdhHttp.jsonPrefix, function(d) {
            $scope.pool = d;
            $scope.poolEntries = [];

            function fetchDocumentHead(ix : number, dag : Types.Content) : void {
                // FIXME: factor out getting from DAG to head version.
                var dagPS = dag.data['P.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhHttp.get(headPath).then(function(headContent) {
                        if (ix in $scope.poolEntries) {
                            $scope.poolEntries[ix].content = headContent;
                        } else {
                            $scope.poolEntries[ix] = {
                                viewmode: 'list',
                                path: headPath,
                                content: headContent,
                            }
                        }
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
                        adhCache.subscribe(path, (dag) => fetchDocumentHead(ix, dag));
                    })(ix);
                }
            }

            init();
        });
    });


    app.controller('AdhDocumentDetail', function(adhHttp : AdhHttp.IService,
                                                 adhCache    : AdhCache.IService,
                                                 $scope : IDocumentDetailScope,
                                                 $rootScope : ng.IScope) : void {

        this.showTitle = function() {
            $scope.doc.viewmode = 'list';
        }

        this.showDetailEdit = function() {
            $scope.doc.previously = Util.deepcp($scope.doc);
            $scope.doc.viewmode = 'edit';
        }

        this.showDetailReset = function() {
            if ('previously' in $scope.doc)
                $scope.doc = $scope.doc.previously;
            $scope.doc.viewmode = 'display';
        }

        this.showDetailSave = function() {
            var oldVersionPath : string = $scope.doc.previously.path;
            if (typeof oldVersionPath == 'undefined') {
                console.log($scope.doc.previously);
                throw 'showDetailSave: no previous path!'
            }
            adhHttp.postNewVersion(oldVersionPath, $scope.doc.content, function() {});
            $scope.doc.viewmode = 'display';
        }
    });


    app.controller('AdhParagraphDetail', function(adhHttp   : AdhHttp.IService,
                                                  adhCache  : AdhCache.IService,
                                                  $scope    : IParagraphDetailScope) : void
    {
        adhCache.subscribe($scope.parref.path, (content) => $scope.parcontent = content);

/*


  FIXME: i need to do more thinking to get this right.  the list of
  fetched paragraphs (as opposed to paragraph references) should only
  appear in this scope, not in the one above!

        // console.log('paragraph scope: ' + $scope.$id + ' of parent: ' + $scope.$parent.$parent.$id);
        // $scope.viewmode = () => { return $scope.doc.viewmode };
        // $scope.paragraph;
        // $scope.$watch($scope.doc.viewmode);


        this.showDetailEdit = function() {
            $scope.model.previously = Util.deepcp($scope.model);
        }

        this.showDetailReset = function() {
            if ('previously' in $scope.model)
                delete $scope.model.previously;
        }

        this.showDetailSave = function() {
            var oldVersionPath : string = $scope.model.previously.path;
            if (typeof oldVersionPath == 'undefined') {
                console.log($scope.model.previously);
                throw 'showDetailSave: no previous path!'
            }
            adhHttp.postNewVersion(oldVersionPath, $scope.model.content, function() {});
            this.showDetailReset($scope.model);
        }
*/
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
            templateUrl: templatePath + '/P/IDocument/Detail.html',
        }
    });


    app.directive('adhParagraphDetail', function() {
        return {
            restrict: 'E',
            templateUrl: templatePath + '/P/IParagraph/Detail.html',
        }
    });


    // get going

    angular.bootstrap(document, ['NGAD']);

}
