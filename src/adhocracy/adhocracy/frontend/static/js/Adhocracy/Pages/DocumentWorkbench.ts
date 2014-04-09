/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require("angular");
import _ = require("underscore");

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import Css = require("Adhocracy/Css");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");
import AdhCache = require("Adhocracy/Services/Cache");

import Resources = require("Adhocracy/Resources");

var templatePath : string = "/frontend_static/templates";
var appPrefix : string = "/app";


// contents of the resource with view mode.
interface IDocument<Data> {
    viewmode : string;
    content  : Types.Content<Data>;
}

interface IDocumentWorkbenchScope<Data> extends ng.IScope {
    pool            : Types.Content<Data>;
    poolEntries     : IDocument<Data>[];
    doc             : IDocument<Data>;  // (iterates over document list with ng-repeat)
    insertParagraph : any;
}

interface IDocumentDetailScope<Data> extends IDocumentWorkbenchScope<Data> {
    list    : () => void;
    display : () => void;
    edit    : () => void;
    reset   : () => void;
    commit  : () => void;
}

interface IParagraphDetailScope<Data> extends IDocumentDetailScope<Data> {
    parref      : Types.Reference;
    parcontent  : Types.Content<Data>;
}

// FIXME: consider using isolated scopes in order to avoid inheriting
// model data.

export function run<Data>() {
    var app = angular.module("NGAD", []);


    // services

    app.factory("adhHttp",   ["$http",                                    AdhHttp.factory]);

    // FIXME: web sockets and cache services are defunct
    // app.factory("adhWS",     ["adhHttp",                                  AdhWS.factory]);
    // app.factory("adhCache",  ["adhHttp", "adhWS", "$q", "$cacheFactory",  AdhCache.factory]);


    // filters

    app.filter("viewFilterList", [ function() {
        return function(obj : Types.Content<Data>) : string {
            return obj.data["adhocracy.sheets.document.IDocument"].title;
        };
    }]);


    // controllers

    app.controller("AdhDocumentTOC",
                   ["adhHttp", "$scope",
                    function(adhHttp  : AdhHttp.IService<Resources.HasIDocumentSheet>,
                             $scope   : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>) : void
    {
        $scope.insertParagraph = function (proposalVersion: Types.Content<Resources.HasIDocumentSheet>) {
            $scope.poolEntries.push({ viewmode: "list", content: proposalVersion });
        };

        console.log("TOC: " + $scope.$id);

        adhHttp.get(AdhHttp.jsonPrefix).then((pool) => {
            $scope.pool = pool;
            $scope.poolEntries = [];

            // FIXME: factor out getting the head version of a DAG.

            function fetchDocumentHead(n : number, dag : Types.Content<Resources.HasIDocumentSheet>) : void {
                var dagPS = dag.data["adhocracy.sheets.versions.IVersions"].elements;
                if (dagPS.length > 0) {
                    var headPath = Resources.newestVersion(dagPS); //FIXME: backend should have LAST
                    adhHttp.get(headPath).then((headContent) => {
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
                var dagRefs : string[] = pool.data["adhocracy.sheets.pool.IPool"].elements;
                for (var dagRefIx in dagRefs) {
                    (function(dagRefIx : number) {
                        var dagRefPath : string = dagRefs[dagRefIx];
                        adhHttp.get(dagRefPath).then((dag) => fetchDocumentHead(dagRefIx, dag));
                    })(dagRefIx);
                }
            }

            init();
        });
    }]);


    app.controller("AdhDocumentDetail",
                   ["adhHttp", "$scope",
                    function(adhHttp  : AdhHttp.IService<Data>,
                             $scope   : IDocumentDetailScope<Data>) : void
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
            adhHttp.get($scope.doc.content.path).then((obj) => { $scope.doc.content = obj; });
            $scope.doc.viewmode = "display";
        };

        $scope.commit = function() {
            console.log("doc-commit: ", $scope.doc, $scope.doc.content.path);

            adhHttp.postNewVersion($scope.doc.content.path, $scope.doc.content);

            $scope.$broadcast("commit");
            $scope.doc.viewmode = "display";
        };
    }]);


    app.controller("AdhParagraphDetail",
                   ["adhHttp", "$scope",
                    function(adhHttp  : AdhHttp.IService<Resources.HasIDocumentSheet>,
                             $scope   : IParagraphDetailScope<Resources.HasIDocumentSheet>) : void
    {
        function update(content : Types.Content<any>) {
            console.log("par-update: " + $scope.parref.path);
            $scope.parcontent = content;
        }

        function commit(event, ...args) {
            console.log("par-commit: " + $scope.parref.path);
            adhHttp.postNewVersion($scope.parcontent.path, $scope.parcontent);
        }

        // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
        adhHttp.get($scope.parref.path).then(update);

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

    app.directive("adhEditDocumentSheet", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/IDocument/Edit.html",
            scope: {
                sheet: "=",
            },
        };
    });

    app.directive("adhShowDocumentSheet", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/IDocument/Show.html",
            scope: {
                sheet: "="
            },
        };
    });

    app.directive("adhEditProposalVersionResource", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/Edit.html",
            scope: {
                resource: "="
            },
        };
    });

    app.directive("adhNewProposal", ["$http", "$q", function($http: ng.IHttpService, $q : ng.IQService) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/newProposal.html",
            scope: {
                onNewProposal: "="
            },  //isolates this scope, i.e. this $scope does not ihnerit from any parent $scope
            controller: function($scope) {
                $scope.proposalVersion = (new Resources.Resource("adhocracy.resources.proposal.IProposalVersion"))
                                              .addIDocument("", "", []);

                $scope.paragraphVersions = [];

                $scope.pushParagraphVersion = function () {
                    $scope.paragraphVersions.push(new Resources.Resource("adhocracy.resources.paragraph.IParagraphVersion")
                                                      .addIParagraph(""));
                };

                $scope.commit = function() {
                    var proposalPromise = Resources.postProposal($http, $q, $scope.proposalVersion, $scope.paragraphVersions);
                    proposalPromise.then( (resp) =>
                        $http.get(resp.data.path).then( (respGet =>
                            $scope.onNewProposal(respGet.data))
                        )
                    );
                }
            }
        };
    }]);


    // get going

    angular.bootstrap(document, ["NGAD"]);
}
