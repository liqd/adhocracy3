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
    details     : Types.Content[];
    previously ?: IDocument;
}

interface IDocumentTOCScope extends ng.IScope {
    pool : Types.Content;
    poolEntries : IDocument[];
}

interface IDocumentDetailScope extends IDocumentTOCScope {
    // FIXME: i want this interface to extend ng.IScope instead!
    entry : IDocument;  // FIXME: this is just wrong!  clean up the scope!
    doc : IDocument;
}


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
                var dagPS = dag.data['P.IDAG'];
                if (dagPS.versions.length > 0) {
                    var dagPath = dag.path;
                    var headPath = dagPS.versions[0].path;
                    adhHttp.get(headPath).then(function(headContent) {
                        var paragraphs = [];
                        fetchDocumentDetails(headContent,
                                             (ix, paragraph) => { paragraphs[ix] = paragraph });

                        if (ix in $scope.poolEntries) {
                            $scope.poolEntries[ix].content = headContent;
                            $scope.poolEntries[ix].details = paragraphs;
                        } else {
                            $scope.poolEntries[ix] = {
                                viewmode: 'list',
                                path: headPath,
                                content: headContent,
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
                        adhCache.subscribe(path, (dag) => fetchDocumentHead(ix, dag));
                    })(ix);
                }
            }

            init();
        });
    });


    app.controller('AdhDocumentDetail', function(adhHttp : AdhHttp.IService,
                                                 $scope : IDocumentDetailScope,
                                                 $rootScope : ng.IScope) : void {

        // FIXME: entry should not be visible from TOC $scope.  is
        // there a better way to pass it into current $scope?
        // http://docs.angularjs.org/guide/scope?_escaped_fragment_=
        console.log('detail: ' + $scope.$id + ' of parent: ' + $scope.$parent.$parent.$id);
        $scope.doc = $scope.entry;
        delete $scope.entry;

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


    app.controller('AdhParagraphDetail', function(adhHttp : AdhHttp.IService, $scope : any) : void {

        // FIXME: see FIXME at beginning of AdhDocumentDetail controller.
        console.log('paragraph scope: ' + $scope.$id + ' of parent: ' + $scope.$parent.$parent.$id);
        $scope.viewmode = () => { return $scope.doc.viewmode };
        // $scope.paragraph;

        $scope.$watch($scope.doc.viewmode);

/*

  FIXME: i need to do more thinking to get this right.

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
