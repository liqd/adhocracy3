import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhImage = require("../Image/Image");
import AdhInject = require("../Inject/Inject");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhSticky = require("../Sticky/Sticky");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import AdhCommentAdapter = require("../Comment/Adapter");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIMetadata = require("../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIImageReference = require("../../Resources_/adhocracy_core/sheets/image/IImageReference");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/Document";


export interface IParagraph {
    body : string;
    commentCount? : number;
    path? : string;
    selectedState? : string;
}

export interface IScope extends angular.IScope {
    path? : string;
    options : AdhHttp.IOptions;
    errors? : AdhHttp.IBackendErrorItem[];
    data : {
        title : string;
        paragraphs? : IParagraph[];
        commentCountTotal? : number;
        picture? : string;
        creator? : string;
        creationDate? : string;
        modificationDate? : string;
    };
    selectedState? : string;
    resource: any;

    documentVersion? : RIDocumentVersion;
    paragraphVersions? : RIParagraphVersion[];
}

export interface IFormScope extends IScope {
    showError;
    addParagraph() : void;
    submit() : angular.IPromise<any>;
    cancel() : void;
    documentForm : any;
}

export var highlightSelectedParagraph = (
    commentableUrl : string,
    scope : IScope) => {
    if (scope.data) {
        _.forEach(scope.data.paragraphs, (paragraph) => {
            if (!commentableUrl) {
                paragraph.selectedState = "";
            } else if (paragraph.path === commentableUrl) {
                paragraph.selectedState = "is-selected";
            } else {
                paragraph.selectedState = "is-not-selected";
            }
        });
    }
};

export var bindPath = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState? : AdhTopLevelState.Service
) => (
    scope : IScope,
    pathKey : string = "path"
) : Function => {
    var commentableAdapter = new AdhCommentAdapter.ListingCommentableAdapter();

    return scope.$watch(pathKey, (path : string) => {
        if (path) {
            adhHttp.get(path).then((documentVersion : RIDocumentVersion) => {
                var paragraphPaths : string[] = documentVersion.data[SIDocument.nick].elements;
                var paragraphPromises = _.map(paragraphPaths, (path) => adhHttp.get(path));

                return $q.all(paragraphPromises).then((paragraphVersions : RIParagraphVersion[]) => {
                    var paragraphs = _.map(paragraphVersions, (paragraphVersion) => {
                        return {
                            body: paragraphVersion.data[SIParagraph.nick].text,
                            commentCount: commentableAdapter.totalCount(paragraphVersion),
                            path: paragraphVersion.path
                        };
                    });

                    scope.documentVersion = documentVersion;
                    scope.paragraphVersions = paragraphVersions;

                    scope.data = {
                        title: documentVersion.data[SITitle.nick].title,
                        paragraphs: paragraphs,
                        // FIXME: DefinitelyTyped
                        commentCountTotal: (<any>_).sum(_.map(paragraphs, "commentCount")),
                        modificationDate: documentVersion.data[SIMetadata.nick].modification_date,
                        creationDate: documentVersion.data[SIMetadata.nick].creation_date,
                        creator: documentVersion.data[SIMetadata.nick].creator,
                        picture: documentVersion.data[SIImageReference.nick].picture
                    };

                    // FIXME: This probably isn't the right place for this also topLevelState
                    // had to be included in this function just for this
                    if (adhTopLevelState) {
                        highlightSelectedParagraph(adhTopLevelState.get("commentableUrl"), scope);
                    }
                });
            });
        }
    });
};

export var postCreate = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    poolPath : string
) : angular.IPromise<RIDocumentVersion> => {
    var doc = new RIDocument({preliminaryNames: adhPreliminaryNames});
    doc.parent = poolPath;

    var paragraphItems = [];
    var paragraphVersions = [];

    _.forEach(scope.data.paragraphs, (paragraph) => {
        var item = new RIParagraph({preliminaryNames: adhPreliminaryNames});
        item.parent = doc.path;

        var version = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
        version.parent = item.path;
        version.data[SIVersionable.nick] = new SIVersionable.Sheet({
            follows: [item.first_version_path]
        });
        version.data[SIParagraph.nick] = new SIParagraph.Sheet({
            text: paragraph.body
        });

        paragraphItems.push(item);
        paragraphVersions.push(version);
    });

    var documentVersion = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
    documentVersion.parent = doc.path;
    documentVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [doc.first_version_path]
    });
    documentVersion.data[SIDocument.nick] = new SIDocument.Sheet({
        description: "",
        elements: <string[]>_.map(paragraphVersions, "path")
    });
    documentVersion.data[SITitle.nick] = new SITitle.Sheet({
        title: scope.data.title
    });

    return adhHttp.deepPost(<any[]>_.flatten([doc, documentVersion, paragraphItems, paragraphVersions]))
        .then((result) => result[1]);
};

export var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    oldVersion : RIDocumentVersion,
    oldParagraphVersions : RIParagraphVersion[]
) : angular.IPromise<RIDocumentVersion> => {
    // This function assumes that paragraphs can not be reordered or deleted
    // and that new paragraphs are always appended to the end.

    var documentPath = AdhUtil.parentPath(oldVersion.path);

    var paragraphItems : RIParagraph[] = [];
    var paragraphVersions : RIParagraphVersion[] = [];
    var paragraphRefs : string[] = [];

    var paragraphVersion : RIParagraphVersion;

    _.forEach(scope.data.paragraphs, (paragraph : IParagraph, index : number) => {
        if (index >= oldParagraphVersions.length) {
            var item = new RIParagraph({preliminaryNames: adhPreliminaryNames});
            item.parent = documentPath;

            paragraphVersion = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
            paragraphVersion.parent = item.path;
            paragraphVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
                follows: [item.first_version_path]
            });
            paragraphVersion.data[SIParagraph.nick] = new SIParagraph.Sheet({
                text: paragraph.body
            });
            paragraphVersion.root_versions = [oldVersion.path];

            paragraphItems.push(item);
            paragraphVersions.push(paragraphVersion);
            paragraphRefs.push(paragraphVersion.path);
        } else {
            var oldParagraphVersion = oldParagraphVersions[index];

            if (paragraph.body !== oldParagraphVersion.data[SIParagraph.nick].text) {
                paragraphVersion = new RIParagraphVersion({preliminaryNames: adhPreliminaryNames});
                paragraphVersion.parent = AdhUtil.parentPath(oldParagraphVersion.path);
                paragraphVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
                    follows: [oldParagraphVersion.path]
                });
                paragraphVersion.data[SIParagraph.nick] = new SIParagraph.Sheet({
                    text: paragraph.body
                });
                paragraphVersion.root_versions = [oldVersion.path];

                paragraphVersions.push(paragraphVersion);
                paragraphRefs.push(paragraphVersion.path);
            } else {
                paragraphRefs.push(oldParagraphVersion.path);
            }
        }
    });

    var documentVersion = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
    documentVersion.parent = documentPath;
    documentVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
        follows: [oldVersion.path]
    });
    documentVersion.data[SIDocument.nick] = new SIDocument.Sheet({
        description: "",
        elements: paragraphRefs
    });
    documentVersion.data[SITitle.nick] = new SITitle.Sheet({
        title: scope.data.title
    });
    // FIXME: workaround for a backend bug
    var oldImageReferenceSheet = oldVersion.data[SIImageReference.nick];
    if (oldImageReferenceSheet.picture) {
        documentVersion.data[SIImageReference.nick] = oldImageReferenceSheet;
    }

    return adhHttp.deepPost(<any[]>_.flatten([documentVersion, paragraphItems, paragraphVersions]))
        .then((result) => result[0]);
};

export var detailDirective = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath($q, adhHttp, adhTopLevelState)(scope);
            scope.$on("$destroy", adhTopLevelState.on("commentableUrl", (commentableUrl) => {
                highlightSelectedParagraph(adhTopLevelState.get("commentableUrl"), scope);
            }));
        }
    };
};

export var listItemDirective = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath($q, adhHttp)(scope);

            scope.$on("$destroy", adhTopLevelState.on("documentUrl", (documentVersionUrl) => {
                if (!documentVersionUrl) {
                    scope.selectedState = "";
                } else if (documentVersionUrl === scope.path) {
                    scope.selectedState = "is-selected";
                } else {
                    scope.selectedState = "is-not-selected";
                }
            }));
        }
    };
};

export var listingDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.contentType = RIDocumentVersion.content_type;
        }
    };
};

export var createDirective = (
    $location : angular.ILocationService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid,
    adhResourceUrlFilter
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.data = {
                title: "",
                paragraphs: [{
                    body: ""
                }]
            };
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            scope.cancel = () => {
                var processUrl = adhTopLevelState.get("processUrl");
                adhTopLevelState.redirectToCameFrom(adhResourceUrlFilter(processUrl));
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path);
                }).then((documentVersion : RIDocumentVersion) => {
                    var itemPath = AdhUtil.parentPath(documentVersion.path);
                    $location.url(adhResourceUrlFilter(itemPath));
                });
            };
        }
    };
};

export var editDirective = (
    $location : angular.ILocationService,
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhShowError,
    adhSubmitIfValid,
    adhResourceUrlFilter
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            bindPath($q, adhHttp)(scope);

            scope.cancel = () => {
                var itemPath = AdhUtil.parentPath(scope.documentVersion.path);
                adhTopLevelState.redirectToCameFrom(adhResourceUrlFilter(itemPath));
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.documentVersion, scope.paragraphVersions);
                }).then((documentVersion : RIDocumentVersion) => {
                    var itemPath = AdhUtil.parentPath(documentVersion.path);
                    $location.url(adhResourceUrlFilter(itemPath));
                });
            };
        }
    };
};


export var moduleName = "adhDocument";

export var register = (angular) => {
    angular
        .module(moduleName, [
            "duScroll",
            "ngMessages",
            AdhAngularHelpers.moduleName,
            AdhHttp.moduleName,
            AdhImage.moduleName,
            AdhInject.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhResourceArea.moduleName,
            AdhResourceWidgets.moduleName,
            AdhSticky.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("document-detail");
            adhEmbedProvider.embeddableDirectives.push("document-create");
            adhEmbedProvider.embeddableDirectives.push("document-edit");
            adhEmbedProvider.embeddableDirectives.push("document-list-item");
        }])
        .directive("adhDocumentDetail", ["$q", "adhConfig", "adhHttp", "adhTopLevelState", detailDirective])
        .directive("adhDocumentCreate", [
            "$location",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            createDirective])
        .directive("adhDocumentEdit", [
            "$location",
            "$q",
            "adhConfig",
            "adhHttp",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            editDirective])
        .directive("adhDocumentListing", ["adhConfig", listingDirective])
        .directive("adhDocumentListItem", [
            "$q", "adhConfig", "adhHttp", "adhTopLevelState", listItemDirective]);
};
