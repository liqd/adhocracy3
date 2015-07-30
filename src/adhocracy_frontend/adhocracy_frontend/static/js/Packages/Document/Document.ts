import AdhAngularHelpers = require("../AngularHelpers/AngularHelpers");
import AdhBadge = require("../Badge/Badge");
import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");
import AdhImage = require("../Image/Image");
import AdhInject = require("../Inject/Inject");
import AdhMapping = require("../Mapping/Mapping");
import AdhMarkdown = require("../Markdown/Markdown");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhSticky = require("../Sticky/Sticky");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import AdhCommentAdapter = require("../Comment/Adapter");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIGeoDocument = require("../../Resources_/adhocracy_core/resources/document/IGeoDocument");
import RIGeoDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IGeoDocumentVersion");
import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIImageReference = require("../../Resources_/adhocracy_core/sheets/image/IImageReference");
import SIMetadata = require("../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SIPoint = require("../../Resources_/adhocracy_core/sheets/geo/IPoint");
import SITitle = require("../../Resources_/adhocracy_core/sheets/title/ITitle");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/Document";


export interface IParagraph {
    body : string;
    commentCount? : number;
    path? : string;
    selectedState? : string;
}

export interface IBadge {
    title : string;
    description : string;
    name : string;
}

export interface IScope extends angular.IScope {
    path? : string;
    hasMap? : boolean;
    hasBadges?: boolean;
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

        // optional features
        coordinates? : number[];
        assignments?: IBadge[];
    };
    selectedState? : string;
    resource: any;

    toggleCreateForm() : void;
    showCreateForm? : boolean;

    documentVersion? : RIDocumentVersion;
    paragraphVersions? : RIParagraphVersion[];
}

export interface IFormScope extends IScope {
    showError;
    addParagraph() : void;
    submit() : angular.IPromise<any>;
    cancel() : void;
    documentForm : any;
    polygon? : number[][];
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
    adhGetBadges? : AdhBadge.IGetBadges,
    adhTopLevelState? : AdhTopLevelState.Service
) => (
    scope : IScope,
    pathKey : string = "path",
    hasMap : boolean = false,
    hasBadges : boolean = false
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

                    if (hasMap) {
                        scope.data.coordinates = documentVersion.data[SIPoint.nick].coordinates;
                    }

                    if (hasBadges) {
                        adhGetBadges(documentVersion).then((assignments) => {
                            scope.data.assignments = assignments;
                        });
                    }

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
    poolPath : string,
    hasMap : boolean = false
) : angular.IPromise<RIDocumentVersion> => {
    const documentClass = hasMap ? RIGeoDocument : RIDocument;
    const documentVersionClass = hasMap ? RIGeoDocumentVersion : RIDocumentVersion;

    var doc = new documentClass({preliminaryNames: adhPreliminaryNames});
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

    var documentVersion = new documentVersionClass({preliminaryNames: adhPreliminaryNames});
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
    if (hasMap && scope.data.coordinates && scope.data.coordinates[0] && scope.data.coordinates[1]) {
        documentVersion.data[SIPoint.nick] = new SIPoint.Sheet({
            coordinates: scope.data.coordinates
        });
    }

    return adhHttp.deepPost(<any[]>_.flatten([doc, documentVersion, paragraphItems, paragraphVersions]))
        .then((result) => result[1]);
};

export var postEdit = (
    adhHttp : AdhHttp.Service<any>,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IFormScope,
    oldVersion : RIDocumentVersion,
    oldParagraphVersions : RIParagraphVersion[],
    hasMap : boolean = false
) : angular.IPromise<RIDocumentVersion> => {
    // This function assumes that paragraphs can not be reordered or deleted
    // and that new paragraphs are always appended to the end.

    var documentPath = AdhUtil.parentPath(oldVersion.path);

    const documentVersionClass = hasMap ? RIGeoDocumentVersion : RIDocumentVersion;

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

    var documentVersion = new documentVersionClass({preliminaryNames: adhPreliminaryNames});
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
    if (hasMap && scope.data.coordinates && scope.data.coordinates[0] && scope.data.coordinates[1]) {
        documentVersion.data[SIPoint.nick] = new SIPoint.Sheet({
            coordinates: scope.data.coordinates
        });
    }
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
    adhGetBadges : AdhBadge.IGetBadges,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@",
            hasMap: "=?",
            hasBadges: "=?"
        },
        link: (scope : IScope) => {
            bindPath($q, adhHttp, adhGetBadges, adhTopLevelState)(scope, undefined, scope.hasMap, scope.hasBadges);
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
    adhGetBadges : AdhBadge.IGetBadges,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ListItem.html",
        scope: {
            path: "@",
            hasMap: "=?",
            hasBadges: "=?"
        },
        link: (scope : IScope) => {
            bindPath($q, adhHttp, adhGetBadges)(scope, undefined, scope.hasMap, scope.hasBadges);

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

export var mapListItemDirective = (
    $q : angular.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhGetBadges : AdhBadge.IGetBadges,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    var directive : angular.IDirective = listItemDirective($q, adhConfig, adhHttp, adhGetBadges, adhTopLevelState);
    var superLink = <Function>directive.link;

    directive.require = "^adhMapListingInternal";
    directive.link = (scope : IScope, element, attrs, mapListing : AdhMapping.MapListingController) => {
        scope.hasMap = true;
        superLink(scope);

        var unregister = scope.$watch("data.coordinates", (coordinates : number[]) => {
            if (typeof coordinates !== "undefined" && coordinates.length === 2) {
                scope.$on("$destroy", mapListing.registerListItem(scope.path, coordinates[1], coordinates[0]));
                unregister();
            }
        });
    };

    return directive;
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
            path: "@",
            hasMap: "=?",
            polygon: "=?"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.data = {
                title: "",
                paragraphs: [{
                    body: ""
                }],
                coordinates: []
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
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path, scope.hasMap);
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
            path: "@",
            hasMap: "=?",
            hasBadges: "=?",
            polygon: "=?"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.showError = adhShowError;

            scope.addParagraph = () => {
                scope.data.paragraphs.push({
                    body: ""
                });
            };

            bindPath($q, adhHttp)(scope, undefined, scope.hasMap);

            scope.cancel = () => {
                var itemPath = AdhUtil.parentPath(scope.documentVersion.path);
                adhTopLevelState.redirectToCameFrom(adhResourceUrlFilter(itemPath));
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return postEdit(adhHttp, adhPreliminaryNames)(scope, scope.documentVersion, scope.paragraphVersions, scope.hasMap);
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
            AdhMapping.moduleName,
            AdhMarkdown.moduleName,
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
        .directive("adhDocumentDetail", ["$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", detailDirective])
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
            "$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", listItemDirective])
        .directive("adhDocumentMapListItem", [
            "$q", "adhConfig", "adhHttp", "adhGetBadges", "adhTopLevelState", mapListItemDirective]);
};
