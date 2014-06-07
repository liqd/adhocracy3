/// <reference path="../../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require("angular");

import Types = require("Adhocracy/Types");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhUser = require("Adhocracy/Services/User");
import AdhConfig = require("Adhocracy/Services/Config");

import Resources = require("Adhocracy/Resources");
import Widgets = require("Adhocracy/Widgets");


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


export function run() {
    "use strict";

    var app = angular.module("adhocracy3SampleFrontend", []);

    AdhUser.register(app, "adhUser", "adhLogin");
    AdhConfig.register(app, "adhConfig");

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
        return function(resource : Types.Content<Resources.HasIDocumentSheet>) : string {
            return resource.data["adhocracy.sheets.document.IDocument"].title;
        };
    }]);


    // widget-based directives

    app.directive("adhListing",
                  ["adhConfig", (adhConfig) =>
                   new Widgets.Listing(new Widgets.ListingPoolAdapter()).createDirective(adhConfig)]);

    app.directive("adhListingElement",
                  ["$q", "adhConfig", ($q, adhConfig) =>
                   new Widgets.ListingElement(new Widgets.ListingElementAdapter($q)).createDirective(adhConfig)]);

    app.directive("adhListingElementTitle",
                  ["$q", "adhHttp", "adhConfig", ($q, adhHttp, adhConfig) =>
                   new Widgets.ListingElement(new Widgets.ListingElementTitleAdapter($q, adhHttp)).createDirective(adhConfig)]);


    // application-specific directives

    app.directive("adhDocumentWorkbench", ["adhConfig", function(adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Pages/DocumentWorkbench.html",
            controller: ["adhHttp", "$scope", "adhUser",
                         function(adhHttp  : AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>,
                                  $scope   : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>,
                                  user     : AdhUser.User) : void
            {
                $scope.insertParagraph = function(proposalVersion: Types.Content<Resources.HasIDocumentSheet>) {
                    $scope.poolEntries.push({ viewmode: "list", content: proposalVersion });
                };

                adhHttp.get(adhConfig.jsonPrefix).then((pool) => {
                    $scope.pool = pool;
                    $scope.poolEntries = [];
                    $scope.user = user;

                    // FIXME: factor out getting the head version of a DAG.

                    var fetchDocumentHead = function(n : number, dag : Types.Content<Resources.HasIDocumentSheet>) : void {
                        var dagPS = dag.data["adhocracy.sheets.versions.IVersions"].elements;
                        if (dagPS.length > 0) {
                            var headPath = Resources.newestVersion(dagPS); // FIXME: backend should have LAST
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
                    for (var i = 0; i < dagRefs.length; i++) {
                        (function(dagRefIx : number) {
                            var dagRefPath : string = dagRefs[dagRefIx];
                            adhHttp.get(dagRefPath).then((dag) => fetchDocumentHead(dagRefIx, dag));
                        })(i);
                    }
                });
            }]
        };
    }]);


    app.directive("adhProposalVersionDetail", ["adhConfig", function(adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/Detail.html",
            scope: {
                content: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Types.Content<any>>,
                                  $scope   : IProposalVersionDetailScope<any>) : void
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
            }]
        };
    }]);

    app.directive("adhProposalVersionEdit", ["adhConfig", function(adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/Edit.html",
            scope: {
                content: "="
            }
        };
    }]);

    app.directive("adhProposalVersionNew", ["$http", "$q", "adhConfig",
                                            function($http: ng.IHttpService, $q : ng.IQService, adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/New.html",
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


    app.directive("adhSectionVersionDetail", ["adhConfig", "RecursionHelper", function(adhConfig: AdhConfig.Type, RecursionHelper) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Resources/ISectionVersion/Detail.html",
            compile: (element) => RecursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Types.Content<Resources.HasISectionSheet>>,
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
            }]
        };
    }]);


    app.directive("adhParagraphVersionDetail", ["adhConfig", function(adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Resources/IParagraphVersion/Detail.html",
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope",
                         function(adhHttp  : AdhHttp.IService<Types.Content<Resources.HasIParagraphSheet>>,
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
            }]
        };
    }]);


    app.directive("adhDocumentSheetEdit", ["$http", "$q", "adhConfig", function($http, $q, adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Sheets/IDocument/Edit.html",
            scope: {
                sheet: "="
            },
            controller: function($scope) {
                var versionPromises = $scope.sheet.elements.map( (path) =>
                    $http.get( decodeURIComponent(path) )
                         .then( (resp) => resp.data )
                );

                $q.all(versionPromises).then( (versions) =>
                    $scope.sectionVersions = versions
                );
            }
        };
    }]);

    app.directive("adhDocumentSheetShow", ["adhConfig", function(adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Sheets/IDocument/Show.html",
            scope: {
                sheet: "="
            }
        };
    }]);


    app.directive("adhParagraphSheetEdit", ["adhConfig", function(adhConfig) {
        return {
            restrict: "E",
            templateUrl: adhConfig.templatePath + "/Sheets/IParagraph/Edit.html",
            scope: {
                sheet: "="
            }
        };
    }]);


    // get going

    angular.bootstrap(document, ["adhocracy3SampleFrontend"]);
}
