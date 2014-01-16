/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require("angular");

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import Css = require("Adhocracy/Css");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");
import AdhCache = require("Adhocracy/Services/Cache");

var templatePath : string = "/static/templates";
var appPrefix : string = "/app";


// the model object that contains the contents of the resource, the
// view mode (and possibly more stuff in the final implementation).
interface IDocument {
    viewmode    : string;
    content     : Types.Content;
}

interface IDocumentWorkbenchScope extends ng.IScope {
    pool : Types.Content;
    poolEntries : IDocument[];
    doc : IDocument;  // (iterates over document list with ng-repeat)
}

interface IDocumentDetailScope extends IDocumentWorkbenchScope {
    list    : () => void;
    display : () => void;
    edit    : () => void;
    reset   : () => void;
    commit  : () => void;
}

interface IParagraphDetailScope extends IDocumentDetailScope {
    parref      : Types.Reference;
    parcontent  : Types.Content;
}

// FIXME: consider using isolated scopes in order to avoid inheriting
// model data.


export function run() {
    var app = angular.module("NGAD", []);


    // services

    app.factory("adhHttp",   ["$http",                                    AdhHttp.factory]);
    app.factory("adhWS",     ["adhHttp",                                  AdhWS.factory]);
    app.factory("adhCache",  ["adhHttp", "adhWS", "$q", "$cacheFactory",  AdhCache.factory]);


    // filters

    app.filter("viewFilterList", [ function() {
        return function(obj : Types.Content) : string {
            return obj.data["P.IDocument"].title;
        };
    }]);


    // controllers

    app.controller("AdhDocumentTOC",
                   ["adhCache", "$scope",
                    function(adhCache    : AdhCache.IService,
                             $scope      : IDocumentWorkbenchScope) : void
    {
        console.log("TOC: " + $scope.$id);

        // FIXME: when and how do i unsubscribe?  (applies to all subscriptions in this module.)

        adhCache.get(AdhHttp.jsonPrefix, true).promise.then(function(pool) {
            $scope.pool = pool;
            $scope.poolEntries = [];

            function fetchDocumentHead(ix : number, dag : Types.Content) : void {
                // FIXME: factor out getting from DAG to head version.
                var dagPS = dag.data["P.IDAG"];
                if (dagPS.versions.length > 0) {
                    var headPath = dagPS.versions[0].path;
                    adhCache.get(headPath, false).promise.then(function(headContent) {
                        if (ix in $scope.poolEntries) {
                            $scope.poolEntries[ix].content = headContent;
                        } else {
                            $scope.poolEntries[ix] = { viewmode: "list", content: headContent };
                        }
                    });
                } else {
                    $scope.poolEntries[ix] = undefined;
                }
            }

            function init() {
                var els : Types.Reference[] = pool.data["P.IPool"].elements;
                for (var ix in els) {
                    (function(ix : number) {
                        var path : string = els[ix].path;
                        adhCache.get(path, true).promise.then((dag : Types.Content) => fetchDocumentHead(ix, dag));
                    })(ix);
                }
            }

            init();
        });
    }]);


    app.controller("AdhDocumentDetail",
                   ["adhCache", "$scope",
                    function(adhCache    : AdhCache.IService,
                             $scope      : IDocumentDetailScope) : void
    {
        $scope.list = function() {
            $scope.doc.viewmode = "list";
        };

        $scope.display = function() {
            $scope.doc.viewmode = "display";
        };

        $scope.edit = function() {
            $scope.doc.viewmode = "edit";
        };

        $scope.reset = function() {
            adhCache.reset($scope.doc.content.path);
            $scope.doc.viewmode = "display";
        };

        $scope.commit = function() {
            console.log("doc-commit: ", $scope.doc.content, $scope.doc.content.path);
            adhCache.commit($scope.doc.content.path);
            $scope.$broadcast("commit");
            $scope.doc.viewmode = "display";
        };
    }]);


    app.controller("AdhParagraphDetail",
                   ["adhCache", "$scope",
                    function(adhCache  : AdhCache.IService,
                             $scope    : IParagraphDetailScope) : void
    {
        function update(content) {
            console.log("par-update: " + $scope.parref.path);
            $scope.parcontent = content;
        }

        function commit(event, ...args) {
            console.log("par-commit: " + $scope.parref.path);
            adhCache.commit($scope.parcontent.path);

            // FIXME: the commit-triggered update will be followed by
            // a redundant update triggered by the web socket event.
            // not sure what's the best way to tweak this.  shouldn't
            // do any harm besides the overhead though.
        }

        // keep pristine copy in sync with cache.
        adhCache.get($scope.parref.path, true).promise.then(update);

        // save working copy on 'commit' event from containing document.
        $scope.$on("commit", commit);
    }]);


    app.directive("adhDocumentWorkbench", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/P/IDocument/Workbench.html",
        };
    });


    app.directive("adhDocumentDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/P/IDocument/Detail.html",
        };
    });


    app.directive("adhParagraphDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/P/IParagraph/Detail.html",
        };
    });


    // get going

    angular.bootstrap(document, ["NGAD"]);

}
