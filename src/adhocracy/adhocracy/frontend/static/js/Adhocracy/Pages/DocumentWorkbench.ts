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
import AdhUser = require("Adhocracy/Services/User");

import Resources = require("Adhocracy/Resources");
import Widgets = require("Adhocracy/Widgets");

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
    user            : AdhUser.User;
}

interface DetailScope<Data> extends ng.IScope {
    viewmode : string;
    content  : Types.Content<Data>;
}

interface DetailRefScope<Data> extends DetailScope<Data> {
    ref      : string;
}

interface IProposalVersionDetailScope<Data> extends DetailScope<Data> {
    list     : () => void;
    display  : () => void;
    edit     : () => void;
    reset    : () => void;
    commit   : () => void;
}


export function run<Data>() {
    var app = angular.module("adhocracy3SampleFrontend", []);

    AdhUser.register(app, "adhUser", "adhLogin");

    // services

    app.factory("RecursionHelper", ["$compile", function($compile) {
        return {
            /**
             * Manually compiles the element, fixing the recursion loop.
             * @param element
             * @param [link] A post-link function, or an object with function(s) registered via pre and post properties.
             * @returns An object containing the linking functions.
             */
            compile: function(element, link) {
                // Normalize the link parameter
                if (jQuery.isFunction(link)) {
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
                    post: function(scope, element) {
                        // Compile the contents
                        if (!compiledContents) {
                            compiledContents = $compile(contents);
                        }
                        // Re-add the compiled contents to the element
                        compiledContents(scope, function(clone) {
                            element.append(clone);
                        });

                        // Call the post-linking function, if any
                        if (link && link.post) {
                            link.post.apply(null, arguments);
                        }
                    }
                };
            }
        };
    }]);


    app.factory("adhHttp", ["$http", AdhHttp.factory]);


    // filters

    app.filter("documentTitle", [ function() {
        return function(resource : Types.Content<Data>) : string {
            return resource.data["adhocracy.sheets.document.IDocument"].title;
        };
    }]);


    // widget-based directives

    app.directive("wdgListing",
                  () => new Widgets.Listing(new Widgets.ListingContainerAdapter()).factory());

    app.directive("wdgListingElement",
                  ["$q", ($q) =>
                   new Widgets.ListingElement(new Widgets.ListingElementAdapter($q)).factory()]);

    app.directive("wdgListingElementTitle",
                  ["$q", "adhHttp", ($q, adhHttp) =>
                   new Widgets.ListingElement(new Widgets.ListingElementTitleAdapter($q, adhHttp)).factory()]);


    // application-specific directives

    app.directive("adhDocumentWorkbench", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Pages/DocumentWorkbench.html",
            controller: ["adhHttp", "$scope", "adhUser",
                         function(adhHttp  : AdhHttp.IService<Resources.HasIDocumentSheet>,
                                  $scope   : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>,
                                  user     : AdhUser.User) : void
            {
                $scope.insertParagraph = function(proposalVersion: Types.Content<Resources.HasIDocumentSheet>) {
                    $scope.poolEntries.push({ viewmode: "list", content: proposalVersion });
                };

                adhHttp.get(AdhHttp.jsonPrefix).then((pool) => {
                    $scope.pool = pool;
                    $scope.poolEntries = [];
                    $scope.user = user;

                    // FIXME: factor out getting the head version of a DAG.

                    var fetchDocumentHead = function(n : number, dag : Types.Content<Resources.HasIDocumentSheet>) : void {
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
                    };

                    var dagRefs : string[] = pool.data["adhocracy.sheets.pool.IPool"].elements;
                    for (var dagRefIx in dagRefs) {
                        (function(dagRefIx : number) {
                            var dagRefPath : string = dagRefs[dagRefIx];
                            adhHttp.get(dagRefPath).then((dag) => fetchDocumentHead(dagRefIx, dag));
                        })(dagRefIx);
                    }
                });
            }],
        };
    });


    app.directive("adhProposalVersionDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/Detail.html",
            scope: {
                content: "=",
                viewmode: "=",
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Data>,
                                  $scope   : IProposalVersionDetailScope<Data>) : void
            {
                $scope.list = function() {
                    $scope.viewmode = "list";
                };

                $scope.display = function() {
                    $scope.viewmode = "display";
                };

                $scope.edit = function() {
                    $scope.viewmode = "edit";
                };

                $scope.reset = function() {
                    adhHttp.get($scope.content.path).then( (content) => {
                        $scope.content = content;
                    });
                    $scope.viewmode = "display";
                };

                $scope.commit = function() {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);

                    $scope.$broadcast("commit");
                    $scope.viewmode = "display";
                };
            }],
        };
    });

    app.directive("adhProposalVersionEdit", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/Edit.html",
            scope: {
                content: "="
            },
        };
    });

    app.directive("adhProposalVersionNew", ["$http", "$q", function($http: ng.IHttpService, $q : ng.IQService) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IProposalVersion/New.html",
            scope: {
                onNewProposal: "="
            },
            controller: function($scope) {
                $scope.proposalVersion = (new Resources.Resource("adhocracy_sample.resources.proposal.IProposalVersion"))
                                              .addIDocument("", "", []);

                $scope.paragraphVersions = [];

                $scope.addParagraphVersion = function() {
                    $scope.paragraphVersions.push(new Resources.Resource("adhocracy_sample.resources.paragraph.IParagraphVersion")
                                                      .addIParagraph(""));
                };

                $scope.commit = function() {
                    Resources.postProposal($http, $q, $scope.proposalVersion, $scope.paragraphVersions).then( (resp) => {
                        $http.get(resp.data.path).then( (respGet) => {
                            $scope.onNewProposal(respGet.data);
                        });
                    });
                };
            }
        };
    }]);


    app.directive("adhSectionVersionDetail", ["RecursionHelper", function(RecursionHelper) {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/ISectionVersion/Detail.html",
            compile: (element) => RecursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "=",
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Resources.HasISectionSheet>,
                                  $scope   : DetailRefScope<Resources.HasISectionSheet>) : void
            {
                var commit = function(event, ...args) {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then( (content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }],
        };
    }]);


    app.directive("adhParagraphVersionDetail", function() {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Resources/IParagraphVersion/Detail.html",
            scope: {
                ref: "=",
                viewmode: "=",
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Resources.HasIParagraphSheet>,
                                  $scope   : DetailRefScope<Resources.HasIParagraphSheet>) : void
            {
                var commit = function(event, ...args) {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then( (content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }],
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

    angular.bootstrap(document, ["adhocracy3SampleFrontend"]);
}
