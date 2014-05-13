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


    app.factory('RecursionHelper', ['$compile', function($compile){
        return {
            /**
             * Manually compiles the element, fixing the recursion loop.
             * @param element
             * @param [link] A post-link function, or an object with function(s) registered via pre and post properties.
             * @returns An object containing the linking functions.
             */
            compile: function(element, link){
                // Normalize the link parameter
                if(jQuery.isFunction(link)){
                    link = { post: link };
                }

                // Break the recursion loop by removing the contents
                var contents = element.contents().remove();
                var compiledContents;
                return {
                    pre: (link && link.pre) ? link.pre : null,
                    /**
                     * Compiles and re-adds the contents
                     */
                    post: function(scope, element){
                        // Compile the contents
                        if(!compiledContents){
                            compiledContents = $compile(contents);
                        }
                        // Re-add the compiled contents to the element
                        compiledContents(scope, function(clone){
                            element.append(clone);
                        });

                        // Call the post-linking function, if any
                        if(link && link.post){
                            link.post.apply(null, arguments);
                        }
                    }
                };
            }
        };
    }]);


    // services

    app.factory("adhHttp", ["$http", AdhHttp.factory]);


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
            templateUrl: templatePath + "/Pages/DocumentWorkbench.html",
        };
    });


    app.directive("adhProposalVersionDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/Detail.html",
        };
    });


    app.directive("adhParagraphVersionDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IParagraphVersion/Detail.html",
        };
    });

    app.directive("adhDocumentSheetEdit", ["$http", "$q", function($http, $q) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/IDocument/Edit.html",
            scope: {
                sheet: "=",
            },
            controller: function($scope) {
                var versionPromises = $scope.sheet.elements.map( (path) =>
                    $http.get( decodeURIComponent(path) )
                         .then( (resp) => resp.data )
                );

                $q.all(versionPromises).then( (versions) =>
                    $scope.sectionVersions = versions
                );
            },
        };
    }]);

    app.directive("adhDocumentSheetShow", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/IDocument/Show.html",
            scope: {
                sheet: "="
            },
        };
    });

    app.directive("adhProposalVersionEdit", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/Edit.html",
            scope: {
                resource: "="
            },
        };
    });

    app.directive("adhProposalVersionNew", ["$http", "$q", function($http: ng.IHttpService, $q : ng.IQService) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/New.html",
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


    app.directive("adhSectionSheetEdit", ["$http", "$q", "RecursionHelper", function($http, $q, RecursionHelper) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/ISection/Edit.html",
            compile: (element) => RecursionHelper.compile(element),
            scope: {
                sheet: "="
            },
            controller: function ($scope) {
                var versionPromises = $scope.sheet.elements.map( (path) =>
                    $http.get(decodeURIComponent(path))
                         .then( (resp) => resp.data )
                );

                $q.all(versionPromises).then( (versions) => {
                    $scope.concreteElements = versions;
                });
            },
        };
    }]);

    app.directive("adhParagraphSheetEdit", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Sheets/IParagraph/Edit.html",
            scope: {
                sheet: "="
            },
        };
    });


    // get going

    angular.bootstrap(document, ["NGAD"]);
}
