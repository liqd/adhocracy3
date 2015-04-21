/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhAbuse = require("../../Abuse/Abuse");
import AdhConfig = require("../../Config/Config");
import AdhHttp = require("../../Http/Http");
import AdhMovingColumns = require("../../MovingColumns/MovingColumns");
import AdhProcess = require("../../Process/Process");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");
import AdhUser = require("../../User/User");

import RICommentVersion = require("../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIKiezkassenProcess = require("../../../Resources_/adhocracy_core/resources/pool/IBasicPool");  // FIXME
import RIProposalVersion = require("../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIComment = require("../../../Resources_/adhocracy_core/sheets/comment/IComment");

var pkgLocation = "/MeinBerlin/Workbench";


export var meinBerlinWorkbenchDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html"
    };
};

export var commentColumnDirective = (
    bindVariablesAndClear : AdhMovingColumns.IBindVariablesAndClear,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            bindVariablesAndClear(scope, column, ["proposalUrl", "commentableUrl"]);
        }
    };
};

export var kiezkassenProposalDetailColumnDirective = (
    bindVariablesAndClear : AdhMovingColumns.IBindVariablesAndClear,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            bindVariablesAndClear(scope, column, ["processUrl", "proposalUrl"]);
        }
    };
};

export var kiezkassenProposalCreateColumnDirective = (
    bindVariablesAndClear : AdhMovingColumns.IBindVariablesAndClear,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            bindVariablesAndClear(scope, column, ["processUrl"]);
        }
    };
};

export var kiezkassenDetailColumnDirective = (
    bindVariablesAndClear : AdhMovingColumns.IBindVariablesAndClear,
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/KiezkassenDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            bindVariablesAndClear(scope, column, ["processUrl"]);
        }
    };
};


export var moduleName = "adhMeinBerlinWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuse.moduleName,
            AdhHttp.moduleName,
            AdhMovingColumns.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName,
            AdhUser.moduleName
        ])
        // FIXME: the following should be specific to kiezkassen process
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RIKiezkassenProcess.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .specific(RIKiezkassenProcess.content_type, "", "", [() => (resource : RIKiezkassenProcess) => {
                    return {
                        processUrl: resource.path
                    };
                }])
                .default(RIKiezkassenProcess.content_type, "create_proposal", "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIKiezkassenProcess.content_type, "create_proposal", "", ["adhHttp", "adhUser", (
                    adhHttp : AdhHttp.Service<any>,
                    adhUser : AdhUser.Service
                ) => (resource : RIKiezkassenProcess) => {
                    return adhUser.ready.then(() => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {
                                    processUrl: resource.path
                                };
                            }
                        });
                    });
                }])
                .default(RIProposalVersion.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIProposalVersion.content_type, "", "", [() => (resource : RIProposalVersion) => {
                    return {
                        proposalUrl: resource.path,
                        processUrl: "/adhocracy"  // FIXME
                    };
                }])
                .default(RIProposalVersion.content_type, "comments", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIProposalVersion.content_type, "comments", "", [() => (resource : RIProposalVersion) => {
                    return {
                        commentableUrl: resource.path,
                        proposalUrl: resource.path,
                        processUrl: "/adhocracy"  // FIXME
                    };
                }])
                .default(RICommentVersion.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIProposalVersion.content_type, "", "", ["adhHttp", "$q", (
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

                    return (resource : RICommentVersion) => {
                        return getCommentableUrl(resource).then((commentable) => {
                            return {
                                commentableUrl: commentable.path,
                                proposalUrl: commentable.path,
                                processUrl: "/adhocracy"  // FIXME
                            };
                        });
                    };
                }]);
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[""] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mein-berlin-workbench></adh-mein-berlin-workbench>");
            }];
        }])
        .directive("adhMeinBerlinWorkbench", ["adhConfig", meinBerlinWorkbenchDirective])
        .directive("adhCommentColumn", ["adhBindVariablesAndClear", "adhConfig", commentColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalDetailColumn", [
            "adhBindVariablesAndClear", "adhConfig", kiezkassenProposalDetailColumnDirective])
        .directive("adhMeinBerlinKiezkassenProposalCreateColumn", [
            "adhBindVariablesAndClear", "adhConfig", kiezkassenProposalCreateColumnDirective])
        .directive("adhMeinBerlinKiezkassenDetailColumn", [
            "adhBindVariablesAndClear", "adhConfig", kiezkassenDetailColumnDirective]);
};
