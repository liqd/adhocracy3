/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import angular = require("angular");

import Types = require("../Types");
import AdhHttp = require("../Services/Http");
import AdhWebSocket = require("../Services/WebSocket");
import AdhUser = require("../Services/User");
import AdhConfig = require("../Services/Config");
import AdhDone = require("../Services/Done");

import Resources = require("../Resources");
import Widgets = require("../Widgets");


/**
 * contents of the resource with view mode.
 */
interface IDocument<Data> {
    viewmode : string;
    content : Types.Content<Data>;
}

interface IDocumentWorkbenchScope<Data> extends ng.IScope {
    pool : Types.Content<Data>;
    poolEntries : IDocument<Data>[];
    doc : IDocument<Data>;  // (iterates over document list with ng-repeat)
    insertParagraph : any;
    user : AdhUser.User;
}

interface DetailScope<Data> extends ng.IScope {
    viewmode : string;
    content : Types.Content<Data>;
}

interface DetailRefScope<Data> extends DetailScope<Data> {
    ref : string;
}

interface IProposalVersionDetailScope<Data> extends DetailScope<Data> {
    list : () => void;
    display : () => void;
    edit : () => void;
    reset : () => void;
    commit : () => void;
}


export var recursionHelper = ($compile) => {
    return {
        /**
         * Manually compiles the element, fixing the recursion loop.
         * @param element
         * @param [link] A post-link function, or an object with function(s) registered via pre and post properties.
         * @returns An object containing the linking functions.
         */
        compile: (element, link) => {
            // Normalize the link parameter
            if (jQuery.isFunction(link)) {
                link = {post: link};
            }

            // Break the recursion loop by removing the contents
            var contents = element.contents().remove();
            var compiledContents;
            return {
                pre: (link && link.pre) ? link.pre : null,
                /**
                 * Compiles and re-adds the contents
                 */
                post: (scope, element) => {
                    // Compile the contents
                    if (!compiledContents) {
                        compiledContents = $compile(contents);
                    }
                    // Re-add the compiled contents to the element
                    compiledContents(scope, (clone) => {
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
};

export var filterDocumentTitle = () => {
    return (resource : Types.Content<Resources.HasIDocumentSheet>) : string => {
        return resource.data["adhocracy.sheets.document.IDocument"].title;
    };
};

export var adhDocumentWorkbench = (adhConfig: AdhConfig.Type, adhResources: Resources.Service) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Pages/DocumentWorkbench.html",
        controller: ["adhHttp", "$scope", "adhUser", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>,
            $scope : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>,
            user : AdhUser.User
        ) : void => {
            $scope.insertParagraph = (proposalVersion: Types.Content<Resources.HasIDocumentSheet>) => {
                $scope.poolEntries.push({viewmode: "list", content: proposalVersion});
            };

            adhHttp.get(adhConfig.jsonPrefix).then((pool) => {
                $scope.pool = pool;
                $scope.poolEntries = [];
                $scope.user = user;

                // FIXME: factor out getting the head version of a DAG.

                var fetchDocumentHead = (n : number, dag : Types.Content<Resources.HasIDocumentSheet>) : ng.IPromise<void> => {
                    return adhResources.getNewestVersionPath(dag.path)
                        .then((headPath) => adhHttp.get(headPath))
                        .then((headContent) => {
                            if (n in $scope.poolEntries) {
                                // leave original headContentRef intact,
                                // just replace subscription handle and
                                // content object.
                                $scope.poolEntries[n].content = headContent;
                            } else {
                                // bind original headContentRef to model.
                                $scope.poolEntries[n] = {viewmode: "list", content: headContent};
                            }
                        });
                };

                var dagRefs : string[] = pool.data["adhocracy.sheets.pool.IPool"].elements;
                for (var i = 0; i < dagRefs.length; i++) {
                    ((dagRefIx : number) => {
                        var dagRefPath : string = dagRefs[dagRefIx];
                        adhHttp.get(dagRefPath).then((dag) => fetchDocumentHead(dagRefIx, dag));
                    })(i);
                }
            });
        }]
    };
};

export var adhProposalVersionDetail = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/Detail.html",
        scope: {
            content: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<any>>,
            $scope : IProposalVersionDetailScope<any>
        ) : void => {
            $scope.list = () => {
                $scope.viewmode = "list";
            };

            $scope.display = () => {
                $scope.viewmode = "display";
            };

            $scope.edit = () => {
                $scope.viewmode = "edit";
            };

            $scope.reset = () => {
                adhHttp.get($scope.content.path).then((content) => {
                    $scope.content = content;
                });
                $scope.viewmode = "display";
            };

            $scope.commit = () => {
                adhHttp.postNewVersion($scope.content.path, $scope.content);

                $scope.$broadcast("commit");
                $scope.viewmode = "display";
            };
        }]
    };
};

export var adhProposalVersionEdit = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/Edit.html",
        scope: {
            content: "="
        }
    };
};

export var adhProposalVersionNew = (
    adhHttp: ng.IHttpService,
    adhConfig: AdhConfig.Type,
    adhResources: Resources.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Resources/IProposalVersion/New.html",
        scope: {
            onNewProposal: "="
        },
        controller: ($scope) => {
            $scope.proposalVersion = (new Resources.Resource("adhocracy_sample.resources.proposal.IProposalVersion"))
                .addIDocument("", "", []);

            $scope.paragraphVersions = [];

            $scope.addParagraphVersion = () => {
                $scope.paragraphVersions.push(new Resources.Resource("adhocracy_sample.resources.paragraph.IParagraphVersion")
                                              .addIParagraph(""));
            };

            $scope.commit = () => {
                adhResources.postProposalWithParagraphs($scope.proposalVersion, $scope.paragraphVersions).then((resp) => {
                    adhHttp.get(resp.path).then((respGet) => {
                        $scope.onNewProposal(respGet);
                    });
                });
            };
        }
    };
};

export var adhSectionVersionDetail = (adhConfig: AdhConfig.Type, RecursionHelper) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Resources/ISectionVersion/Detail.html",
        compile: (element) => RecursionHelper.compile(element),
        scope: {
            ref: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasISectionSheet>>,
            $scope : DetailRefScope<Resources.HasISectionSheet>
        ) : void => {
            var commit = (event, ...args) => {
                adhHttp.postNewVersion($scope.content.path, $scope.content);
            };

            // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
            adhHttp.get($scope.ref).then((content) => {
                $scope.content = content;
            });

            // save working copy on 'commit' event from containing document.
            $scope.$on("commit", commit);
        }]
    };
};

export var adhParagraphVersionDetail = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Resources/IParagraphVersion/Detail.html",
        scope: {
            ref: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasIParagraphSheet>>,
            $scope : DetailRefScope<Resources.HasIParagraphSheet>
        ) : void => {
            var commit = (event, ...args) => {
                adhHttp.postNewVersion($scope.content.path, $scope.content);
            };

            // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
            adhHttp.get($scope.ref).then((content) => {
                $scope.content = content;
            });

            // save working copy on 'commit' event from containing document.
            $scope.$on("commit", commit);
        }]
    };
};

export var adhDocumentSheetEdit = (adhHttp, $q, adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Sheets/IDocument/Edit.html",
        scope: {
            sheet: "="
        },
        controller: ($scope) => {
            var versionPromises = $scope.sheet.elements.map((path) =>
                                                            adhHttp.get(decodeURIComponent(path))
                                                            .then((resp) => resp.data)
                                                           );

            $q.all(versionPromises).then((versions) =>
                                         $scope.sectionVersions = versions
                                        );
        }
    };
};

export var adhDocumentSheetShow = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Sheets/IDocument/Show.html",
        scope: {
            sheet: "="
        }
    };
};

export var adhParagraphSheetEdit = (adhConfig) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.templatePath + "/Sheets/IParagraph/Edit.html",
        scope: {
            sheet: "="
        }
    };
};

export var run = () => {
    "use strict";

    var app = angular.module("adhocracy3SampleFrontend", []);

    app.service("adhResources", Resources.Service);

    app.service("adhUser", AdhUser.User);
    app.directive("adhLogin", ["adhUser", AdhUser.loginDirective]);
    app.factory("adhConfig", () => AdhConfig.config);
    app.factory("adhDone", AdhDone.factory);

    app.factory("recursionHelper", ["$compile", recursionHelper]);

    app.factory("adhHttp", ["$http", AdhHttp.factory]);
    app.factory("adhWebSocket", ["adhConfig", AdhWebSocket.factory]);

    app.filter("documentTitle", [filterDocumentTitle]);

    app.directive("adhListing",
        ["adhConfig", (adhConfig) =>
            new Widgets.Listing(new Widgets.ListingPoolAdapter()).createDirective(adhConfig)]);

    app.directive("adhListingElement",
        ["$q", "adhConfig", ($q, adhConfig) =>
            new Widgets.ListingElement(new Widgets.ListingElementAdapter($q)).createDirective(adhConfig)]);

    app.directive("adhListingElementTitle",
        ["$q", "adhHttp", "adhConfig", ($q, adhHttp, adhConfig) =>
            new Widgets.ListingElement(new Widgets.ListingElementTitleAdapter($q, adhHttp)).createDirective(adhConfig)]);

    app.directive("adhWebSocketTest",
        ["$timeout", "adhConfig", "adhWebSocket", ($timeout, adhConfig, adhWebSocket) =>
            new AdhWebSocket.WebSocketTest().createDirective($timeout, adhConfig, adhWebSocket)]);


    // application-specific (local) directives

    app.directive("adhDocumentWorkbench", ["adhConfig", "adhResources", adhDocumentWorkbench]);
    app.directive("adhProposalVersionDetail", ["adhConfig", adhProposalVersionDetail]);
    app.directive("adhProposalVersionEdit", ["adhConfig", adhProposalVersionEdit]);
    app.directive("adhProposalVersionNew", ["adhHttp", "adhConfig", "adhResources", adhProposalVersionNew]);
    app.directive("adhSectionVersionDetail", ["adhConfig", "recursionHelper", adhSectionVersionDetail]);
    app.directive("adhParagraphVersionDetail", ["adhConfig", adhParagraphVersionDetail]);
    app.directive("adhDocumentSheetEdit", ["adhHttp", "$q", "adhConfig", adhDocumentSheetEdit]);
    app.directive("adhDocumentSheetShow", ["adhConfig", adhDocumentSheetShow]);
    app.directive("adhParagraphSheetEdit", ["adhConfig", adhParagraphSheetEdit]);


    // get going

    angular.bootstrap(document, ["adhocracy3SampleFrontend"]);
};
