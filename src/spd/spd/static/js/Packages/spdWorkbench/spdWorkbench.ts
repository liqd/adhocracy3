/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhComment = require("../Comment/Comment");
import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhMovingColumns = require("../MovingColumns/MovingColumns");
import AdhPermissions = require("../Permissions/Permissions");
import AdhProcess = require("../Process/Process");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhSPDDocument = require("../spdDocument/spdDocument");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import RIComment = require("../../Resources_/adhocracy_core/resources/comment/IComment");
import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RIParagraph = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import RIProcess = require("../../Resources_/adhocracy_core/resources/process/IProcess");
import SIComment = require("../../Resources_/adhocracy_core/sheets/comment/IComment");
import SIParagraph = require("../../Resources_/adhocracy_core/sheets/document/IParagraph");

var pkgLocation = "/spdWorkbench";


export var spdWorkbenchDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
        }
    };
};


export var commentColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["documentUrl", "commentableUrl"]);
        }
    };
};

export var spdDocumentDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/SpdDocumentDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "documentUrl"]);
            adhPermissions.bindScope(scope, () => scope.documentUrl && AdhUtil.parentPath(scope.documentUrl), "proposalItemOptions");
        }
    };
};

export var spdDocumentCreateColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/SpdDocumentCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
        }
    };
};

export var spdDocumentEditColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/SpdDocumentEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "documentUrl"]);
        }
    };
};

export var processDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProcessDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");
        }
    };
};

export var processDetailAnnounceColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    var directive = processDetailColumnDirective(adhConfig);
    directive.templateUrl = adhConfig.pkg_path + pkgLocation + "/ProcessDetailAnnounceColumn.html";
    return directive;
};


export var moduleName = "adhSPDWorkbench";

export var register = (angular) => {
    var processType = RIProcess.content_type;

    angular
        .module(moduleName, [
            AdhComment.moduleName,
            AdhHttp.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName,
            AdhSPDDocument.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-spd-workbench></adh-spd-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RIProcess, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .default(RIProcess, "create_document", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .specific(RIProcess, "create_document", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (resource : RIProcess) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    }])
                .defaultVersionable(RIDocument, RIDocumentVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIDocument, RIDocumentVersion, "", processType, "", [
                    () => (item : RIDocument, version : RIDocumentVersion) => {
                        return {
                            documentUrl: version.path
                        };
                    }])
                .defaultVersionable(RIDocument, RIDocumentVersion, "edit", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIDocument, RIDocumentVersion, "edit", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (item : RIDocument, version : RIDocumentVersion) => {
                        return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {
                                    documentUrl: version.path
                                };
                            }
                        });
                    }])
                .defaultVersionable(RIParagraph, RIParagraphVersion, "comments", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIParagraph, RIParagraphVersion, "comments", processType, "", [
                    () => (item : RIParagraph, version : RIParagraphVersion) => {
                        return {
                            commentableUrl: version.path,
                            documentUrl: version.data[SIParagraph.nick].documents[0]
                        };
                    }])
                .defaultVersionable(RIComment, RICommentVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIComment, RICommentVersion, "", processType, "", ["adhHttp", "$q", (
                    adhHttp : AdhHttp.Service<any>,
                    $q : angular.IQService
                ) => {
                    var getCommentableUrl = (resource) : angular.IPromise<any> => {
                        if (resource.content_type !== RICommentVersion.content_type) {
                            return $q.when(resource);
                        } else {
                            var url = resource.data[SIComment.nick].refers_to;
                            return adhHttp.get(url).then(getCommentableUrl);
                        }
                    };

                    return (item : RIComment, version : RICommentVersion) => {
                        return getCommentableUrl(version).then((commentable) => {
                            return {
                                commentableUrl: commentable.path,
                                documentUrl: commentable.path
                            };
                        });
                    };
                }]);
        }])
        .directive("adhSpdWorkbench", ["adhConfig", "adhTopLevelState", spdWorkbenchDirective])
        .directive("adhCommentColumn", ["adhConfig", commentColumnDirective])
        .directive("adhSpdDocumentDetailColumn", ["adhConfig", "adhPermissions", spdDocumentDetailColumnDirective])
        .directive("adhSpdDocumentCreateColumn", ["adhConfig", spdDocumentCreateColumnDirective])
        .directive("adhSpdDocumentEditColumn", ["adhConfig", spdDocumentEditColumnDirective])
        .directive("adhSpdProcessDetailColumn", ["adhConfig", "adhPermissions", processDetailColumnDirective])
        .directive("adhSpdProcessDetailAnnounceColumn", ["adhConfig", processDetailAnnounceColumnDirective]);
};
