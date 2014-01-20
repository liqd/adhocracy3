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


// contents of the resource with view mode.
interface IDocument {
    viewmode : string;
    content  : Types.Content;
}

interface IDocumentWorkbenchScope extends ng.IScope {
    pool        : Types.Content;
    poolEntries : IDocument[];
    doc         : IDocument;  // (iterates over document list with ng-repeat)
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

        adhCache.get(AdhHttp.jsonPrefix, true, function(pool) {
            $scope.pool = pool;
            $scope.poolEntries = [];

            // FIXME: factor out getting the head version of a DAG.

            function fetchDocumentHead(n : number, dag : Types.Content) : void {
                var dagPS = dag.data["P.IDAG"];
                if (dagPS.versions.length > 0) {
                    var headPath = dagPS.versions[0].path;
                    adhCache.get(headPath, false, function(headContent) {
                        if (n in $scope.poolEntries) {
                            // leave original headContentRef intact,
                            // just replace subscription handle and
                            // content object.
                            $scope.poolEntries[n].content = headContent;
                        } else {
                            // bind original headContentRef to model.
                            $scope.poolEntries[n] = { viewmode: "list", content: headContent };
                        }
                    });
                }
            }

            function init() {
                var dagRefs : Types.Reference[] = pool.data["P.IPool"].elements;
                for (var dagRefIx in dagRefs) {
                    (function(dagRefIx : number) {
                        var dagRefPath : string = dagRefs[dagRefIx].path;
                        adhCache.get(dagRefPath, true, (dag) => fetchDocumentHead(dagRefIx, dag));
                    })(dagRefIx);
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
            adhCache.get($scope.doc.content.path, false, (obj) => { $scope.doc.content = obj; });
            $scope.doc.viewmode = "display";
        };

        $scope.commit = function() {
            console.log("doc-commit: ", $scope.doc, $scope.doc.content.path);
            adhCache.commit($scope.doc.content.path, $scope.doc.content);
            $scope.$broadcast("commit");
            $scope.doc.viewmode = "display";
        };
    }]);


    app.controller("AdhParagraphDetail",
                   ["adhCache", "$scope",
                    function(adhCache  : AdhCache.IService,
                             $scope    : IParagraphDetailScope) : void
    {
        function update(content : Types.Content) {
            console.log("par-update: " + $scope.parref.path);
            $scope.parcontent = content;
        }

        function commit(event, ...args) {
            console.log("par-commit: " + $scope.parref.path);
            adhCache.commit($scope.parcontent.path, $scope.parcontent);

            // FIXME: the commit-triggered update will be followed by
            // a redundant update triggered by the web socket event.
            // not sure what's the best way to tweak this.  shouldn't
            // do any harm besides the overhead though.
        }

        // keep pristine copy in sync with cache.
        adhCache.get($scope.parref.path, true, update);

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
