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


// the model object that contains the contents of the resource, the
// view mode (and possibly more stuff in the final implementation).
interface IDocument {
    mode        : string;
    content     : Types.Content;
    path        : string;
    details     : Types.Content[];
    previously ?: IDocument;
}

function refreshDocument(obj : IDocument,
                         content ?: Types.Content,
                         details ?: Types.Content[]) : IDocument {
    return {
        mode: obj.mode,
        content: (typeof content == 'undefined' ? obj.content : content),
        path: obj.path,
        details: (typeof details == 'undefined' ? obj.details : details),
    };
}

interface IDocumentTOCScope extends ng.IScope {
    pool : Types.Content;
    poolEntries : IDocument[];
}

interface IDocumentDetailScope extends IDocumentTOCScope {
    // FIXME: i want this interface to extend ng.IScope instead!
    entry : IDocument;  // FIXME: this is just wrong!
    model : IDocument;
}


export function run() {
    var app = angular.module('NGAD', []);


    // services

    app.factory('adhHttp', ['$http', AdhHttp.factory]);


    // filters

    app.filter('viewFilterList', [ function() {
        return function(obj : Types.Content) : string {
            return obj.data['P.IDocument'].title;
        };
    }]);


    // controllers

    app.controller('AdhDocumentTOC', function(adhHttp : AdhHttp.IService,
                                              $scope : IDocumentTOCScope,
                                              $rootScope : ng.IScope) {

        console.log('TOC: ' + $scope.$id);

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
                            refreshDocument($scope.poolEntries[ix], headContent, paragraphs);
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
    });


    app.controller('AdhDocumentDetail', function(adhHttp : AdhHttp.IService,
                                                 $scope : IDocumentDetailScope,
                                                 $rootScope : ng.IScope) {

        // FIXME: entry should not be visible from TOC $scope.  is
        // there a better way to pass it into current $scope?
        console.log('detail: ' + $scope.$id + ' of parent: ' + $scope.$parent.$parent.$id);
        $scope.model = $scope.entry;
        delete $scope.entry;

        this.showTitle = function() {
            $scope.model.mode = 'list';
        }

        this.showDetailEdit = function() {
            $scope.model.previously = Util.deepcp($scope.model);
            $scope.model.mode = 'edit';
        }

        this.showDetailReset = function() {
            if ('previously' in $scope.model)
                delete $scope.model.previously;
            $scope.model.mode = 'display';
        }

        this.showDetailSave = function() {
            var oldVersionPath : string = $scope.model.previously.path;
            if (typeof oldVersionPath == 'undefined') {
                console.log($scope.model.previously);
                throw 'showDetailSave: no previous path!'
            }
            adhHttp.postNewVersion(oldVersionPath, $scope.model.content, function() {});

            // FIXME: post updates on paragraphs separately somehow.

            this.showDetailReset($scope.model);
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
            templateUrl: templatePath + '/P/IDocument/Detail.html',
        }
    });


    // get going

    angular.bootstrap(document, ['NGAD']);

}
