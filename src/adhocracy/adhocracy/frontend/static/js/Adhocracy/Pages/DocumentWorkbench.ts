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

var templatePath : string = "/frontend_static/templates";
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

class Resource {
    content_type : string;
    data : Object;
    constructor(content_type: string) {
        this.content_type = content_type;
        this.data = {};
    }
    addISection(title: string, elements: string[]) {
        this.data["adhocracy.sheets.document.ISection"] = {
            title: title,
            elements: elements,
        };
        return this;
    }
    addIDocument(title: string, description: string, elements: string[]) {
        this.data["adhocracy.sheets.document.IDocument"] = {
            title: title,
            description: description,
            elements: elements,
        };
        return this;
    }
    addIVersionable(follows: string[], root_version: string[]) {
        this.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: follows,
            root_version: root_version,
        };
        return this;
    }
    addIName(name: string) {
        this.data["adhocracy.sheets.name.IName"] = {
            name: name,
        };
        return this;
    }
}

class Proposal extends Resource {
    constructor(name?: string) {
        super("adhocracy.resources.proposal.IProposal");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

class Section extends Resource {
    constructor(name?: string) {
        super("adhocracy.resources.section.ISection");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

class SectionVersion extends Resource {
    constructor(title: string, elements: string[], follows: string[], root_version: string[]) {
        super("adhocracy.resources.section.ISectionVersion");
        this.addISection(title, elements)
            .addIVersionable(follows, root_version);
    }
}

//FIXME: backend should have LAST
function newestVersion(versions: string[]) {
    return _.max(versions, (version_path) => parseInt(version_path.match(/\d*$/)[0], 10));
}


export function run() {
    var app = angular.module("NGAD", []);


    // services

    app.factory("adhHttp",   ["$http",                                    AdhHttp.factory]);

    // FIXME: web sockets and cache services are defunct
    // app.factory("adhWS",     ["adhHttp",                                  AdhWS.factory]);
    // app.factory("adhCache",  ["adhHttp", "adhWS", "$q", "$cacheFactory",  AdhCache.factory]);


    // filters

    app.filter("viewFilterList", [ function() {
        return function(obj : Types.Content) : string {
            return obj.data["adhocracy.sheets.document.IDocument"].title;
        };
    }]);


    // controllers

    app.controller("AdhDocumentTOC",
                   ["adhHttp", "$scope",
                    function(adhHttp  : AdhHttp.IService,
                             $scope   : IDocumentWorkbenchScope) : void
    {
        console.log("TOC: " + $scope.$id);

        adhHttp.get(AdhHttp.jsonPrefix).then((pool) => {
            $scope.pool = pool;
            $scope.poolEntries = [];

            // FIXME: factor out getting the head version of a DAG.

            function fetchDocumentHead(n : number, dag : Types.Content) : void {
                var dagPS = dag.data["adhocracy.sheets.versions.IVersions"].elements;
                if (dagPS.length > 0) {
                    var headPath = newestVersion(dagPS); //FIXME: backend should have LAST
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
                    function(adhHttp  : AdhHttp.IService,
                             $scope   : IDocumentDetailScope) : void
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
                    function(adhHttp  : AdhHttp.IService,
                             $scope   : IParagraphDetailScope) : void
    {
        function update(content : Types.Content) {
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


    app.controller("NewProposal",
                   ["$scope", "$http", "$q",
                    function($scope    ,
                             $http     : ng.IHttpService,
                             $q        : ng.IQService) : void
    {
        $scope.proposalVersion = (new Resource("adhocracy.resources.proposal.IProposalVersion"))
                                              .addIDocument("greg", "ewfwef", []);

        $scope.sections = [];

        $scope.pushSection = function () {
            $scope.sections.push({'wrap': ""});  //FIXME: use resource with ISection instead
        };

        $scope.commit = function () {

            var proposalName = $scope.proposalVersion.data['adhocracy.sheets.document.IDocument'].title;

            $http.post("/adhocracy", new Proposal(proposalName)).then( (resp) => {
                var proposalPath = decodeURIComponent(resp.data.path);
                var proposalFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

                var sectionPromises = $scope.sections.map( (text) =>
                    $http.post(proposalPath, new Section()).then( (resp) => {
                        var sectionPath = decodeURIComponent(resp.data.path);
                        var sectionFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

                        return $http.post(sectionPath, new SectionVersion(text.wrap, [], [sectionFirstVersionPath], [proposalPath]));
                    })
                );

                $q.all(sectionPromises).then( (allResp) => {
                    var paths = allResp.map( (resp) => decodeURIComponent(resp.data.path) );

                    $scope.proposalVersion.addIVersionable(paths, [proposalFirstVersionPath]);
                    $http.post(proposalPath, $scope.proposalVersion);
                });
            });
        };

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
