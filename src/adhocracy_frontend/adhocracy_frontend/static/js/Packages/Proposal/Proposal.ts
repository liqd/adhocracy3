/// <reference path="../../../lib/DefinitelyTyped/lodash/lodash.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPreliminaryNames = require("../../Packages/PreliminaryNames/PreliminaryNames");
import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");
import AdhWebSocket = require("../WebSocket/WebSocket");

import ResourcesBase = require("../../ResourcesBase");

import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SISection = require("../../Resources_/adhocracy_core/sheets/document/ISection");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/Document";

/**
 * contents of the resource with view mode.
 */
export interface DetailScope<Data> extends angular.IScope {
    viewmode : string;
    content : ResourcesBase.Resource;
    path : string;
}

export interface DetailRefScope<Data> extends DetailScope<Data> {
    ref : string;
}

export interface IDocumentVersionDetailScope<Data> extends DetailScope<Data> {
    list : () => void;
    display : () => void;
    edit : () => void;
    onCancel : () => void;
    commit : () => void;
    showComments : () => void;
    hideComments : () => void;
}

export class DocumentDetail {
    public createDirective() {
        return {
            restrict: "E",
            template: "<adh-document-version-detail data-content=\"content\" data-viewmode=\"list\"></adh-document-version-detail>",
            scope: {
                path: "="
            },
            controller: ["adhHttp", "adhWebSocket", "$scope", (
                adhHttp : AdhHttp.Service<any>,
                adhWebSocket : AdhWebSocket.Service,
                $scope : DetailScope<RIDocument>
            ) => {
                var fetchAndUpdateContent = (itemPath : string) : void => {
                    adhHttp.getNewestVersionPathNoFork(itemPath)
                        .then((versionPath : string) => adhHttp.get(versionPath))
                        .then((content) => {
                            $scope.content = content;
                        });
                };

                $scope.$on("$destroy", adhWebSocket.register($scope.path, () => {
                    fetchAndUpdateContent($scope.path);
                }));

                fetchAndUpdateContent($scope.path);
            }]
        };
    }
}

export class DocumentVersionDetail {
    public static templateUrl : string = "Document.html";

    public createDirective(adhConfig : AdhConfig.IService) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/" + _class.templateUrl,
            scope: {
                content: "=",
                viewmode: "@"
            },
            controller: ["adhTopLevelState", "adhHttp", "$scope", (
                adhTopLevelState : AdhTopLevelState.Service,
                adhHttp : AdhHttp.Service<ResourcesBase.Resource>,
                $scope : IDocumentVersionDetailScope<any>
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

                $scope.onCancel = () => {
                    adhHttp.get($scope.content.path).then((content) => {
                        $scope.content = content;
                    });
                    $scope.viewmode = "display";
                };

                $scope.commit = () => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);

                    $scope.$broadcast("commit");
                    $scope.viewmode = "display";
                };

                $scope.showComments = () => {
                    adhTopLevelState.set("content2Url", $scope.content.path);
                    adhTopLevelState.set("movingColumns", "is-collapse-show-show");
                };

                $scope.hideComments = () => {
                    adhTopLevelState.set("movingColumns", "is-show-show-hide");
                };
            }]
        };
    }
}

export interface IScopeDocumentVersion {
    content : RIDocumentVersion;
    paragraphVersions : RIParagraphVersion[];
    addParagraphVersion : () => void;
    commit : () => void;
    onNewDocument : (any) => void;
    onCancel : () => void;
    poolPath : string;
    viewmode : string;
}

export class DocumentVersionNew {

    public createDirective(adhHttp : angular.IHttpService, adhConfig : AdhConfig.IService, adhDocument : Service) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Document.html",
            scope: {
                onNewDocument: "=",
                onCancel: "=",
                poolPath: "@"
            },
            controller: ["$scope", "adhPreliminaryNames", (
                $scope : IScopeDocumentVersion,
                adhPreliminaryNames : AdhPreliminaryNames.Service
            ) => {
                $scope.viewmode = "edit";

                $scope.content = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
                $scope.content.data[SIDocument.nick] =
                    new SIDocument.Sheet({
                        title: "",
                        description: "",
                        picture: undefined,
                        elements: []
                    });
                $scope.paragraphVersions = [];

                $scope.addParagraphVersion = () => {
                    var pv = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
                    pv.data[SIParagraph.nick] =
                        new SIParagraph.Sheet({
                            content: "",
                            elements: []
                        });
                    $scope.paragraphVersions.push(pv);
                };

                $scope.commit = () => {
                    adhDocument.postDocumentWithParagraphs($scope.poolPath, $scope.content, $scope.paragraphVersions)
                        .then((resp) => {
                            adhHttp.get(resp.path).then((respGet) => {
                                $scope.onNewDocument(respGet);
                            });
                        });
                };
            }]
        };
    }
}

var explainPreliminaryGetIssue : string = (
    "The version resources for document, sections, and paragraphs are created and rendered into the\n" +
    "DOM before the user clicks on 'safe'.  Once 'safe' is clicked, these resources wake up and some-\n" +
    "how decide they need to be updated.  This update happens before the batch post returns and can\n" +
    "replace the preliminary paths, so there is an exception.  Fix: use ResourceWidgets for what we\n" +
    "currently do manually here."
);

export class SectionVersionDetail {

    public createDirective(adhConfig : AdhConfig.IService, recursionHelper) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Section.html",
            compile: (element) => recursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<ResourcesBase.Resource>,
                $scope : DetailRefScope<SISection.Sheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);
                };

                try {
                    adhHttp.get($scope.ref).then((content) => {
                        $scope.content = content;
                    });
                } catch (msg) {
                    console.log("info: " + msg);
                    console.log("it is safe to ignore this error.  details:\n" + explainPreliminaryGetIssue);
                }

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class ParagraphVersionDetail {

    public createDirective(adhConfig : AdhConfig.IService) {

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/templates/Paragraph.html",
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<ResourcesBase.Resource>,
                $scope : DetailRefScope<SIParagraph.Sheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersionNoFork($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                try {
                    adhHttp.get($scope.ref).then((content) => {
                        $scope.content = content;
                    });
                } catch (msg) {
                    console.log("info: " + msg);
                    console.log("it is safe to ignore this error.  details:\n" + explainPreliminaryGetIssue);
                }

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class Service {
    constructor(
        private adhHttp : AdhHttp.Service<any>,
        private adhPreliminaryNames : AdhPreliminaryNames.Service,
        private $q : angular.IQService
    ) {}


    public postDocumentWithParagraphs(
        poolPath : string,
        documentVersion : RIDocumentVersion,
        paragraphVersions : RIParagraphVersion[]
    ) {
        var _self = this;

        var sectionVersion : RISectionVersion = new RISectionVersion({preliminaryNames: _self.adhPreliminaryNames});
        sectionVersion.data[SISection.nick] =
            new SISection.Sheet({
                title : "single_section",
                elements : [],
                subsections : []
            });

        var name = documentVersion.data[SIDocument.nick].title;
        name = AdhUtil.normalizeName(name);

        // this is the batch-request logic.  it works a bit different
        // from the original logic in that it follows the references
        // down the items and up the versions, rather than going down
        // both.
        //
        // (this comment reference a meeting held earlier today and is
        // meaningless without having been there.  since this function
        // will be refactored away soon, so that should not be a big
        // deal.)

        return _self.adhHttp
            .withTransaction((transaction) : angular.IPromise<ResourcesBase.Resource> => {
                // items
                var postDocument : AdhHttp.ITransactionResult =
                    transaction.post(poolPath, new RIDocument({preliminaryNames: _self.adhPreliminaryNames, name: name}));
                var postSection : AdhHttp.ITransactionResult =
                    transaction.post(postDocument.path, new RISection({preliminaryNames: _self.adhPreliminaryNames, name: "section"}));
                var postParagraphs : AdhHttp.ITransactionResult[] =
                    paragraphVersions.map((paragraphVersion, i) =>
                        transaction.post(
                            postDocument.path,
                            new RIParagraph({preliminaryNames: _self.adhPreliminaryNames, name: "paragraph" + i})));

                // versions
                var postParagraphVersions = paragraphVersions.map((paragraphVersion, i) => {
                    paragraphVersion.data[SIVersionable.nick] =
                        new SIVersionable.Sheet({
                            follows: [postParagraphs[i].first_version_path]
                        });
                    return transaction.post(postParagraphs[i].path, paragraphVersion);
                });

                sectionVersion.data[SIVersionable.nick] =
                    new SIVersionable.Sheet({
                        follows: [postSection.first_version_path]
                    });
                sectionVersion.data[SISection.nick].elements = postParagraphVersions.map((p) => p.path);
                var postSectionVersion = transaction.post(postSection.path, sectionVersion);

                documentVersion.data[SIVersionable.nick] =
                    new SIVersionable.Sheet({
                        follows: [postDocument.first_version_path]
                    });
                documentVersion.data[SIDocument.nick].elements = [postSectionVersion.path];
                var postDocumentVersion : AdhHttp.ITransactionResult = transaction.post(postDocument.path, documentVersion);

                return transaction.commit()
                    .then((postedResources) => {
                        // return the latest document Version
                        return postedResources[postDocumentVersion.index];
                    });
            });
    }
};


export var moduleName = "adhDocument";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhAngularHelpers.moduleName,
            AdhTopLevelState.moduleName,
            AdhWebSocket.moduleName
        ])
        .service("adhDocument", ["adhHttp", "adhPreliminaryNames", "$q", Service])
        .directive("adhDocumentDetail", () => new DocumentDetail().createDirective())
        .directive("adhDocumentVersionDetail",
            ["adhConfig", (adhConfig) => new DocumentVersionDetail().createDirective(adhConfig)])
        .directive("adhDocumentVersionNew",
            ["adhHttp", "adhConfig", "adhDocument", (adhHttp, adhConfig, adhDocument) =>
                new DocumentVersionNew().createDirective(adhHttp, adhConfig, adhDocument)])
        .directive("adhSectionVersionDetail",
            ["adhConfig", "adhRecursionHelper", (adhConfig, adhRecursionHelper) =>
                new SectionVersionDetail().createDirective(adhConfig, adhRecursionHelper)])
        .directive("adhParagraphVersionDetail",
            ["adhConfig", (adhConfig) => new ParagraphVersionDetail().createDirective(adhConfig)]);
};
