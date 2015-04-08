/// <reference path="../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../../Config/Config");
import AdhMovingColumns = require("../../MovingColumns/MovingColumns");
import AdhProcess = require("../../Process/Process");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");

import RICommentVersion = require("../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIKiezkassenProcess = require("../../../Resources_/adhocracy_core/resources/pool/IBasicPool");  // FIXME
import RIProposalVersion = require("../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");

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
            AdhMovingColumns.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName
        ])
        // FIXME: the following should be specific to kiezkassen process
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .default(RIKiezkassenProcess.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .default(RIKiezkassenProcess.content_type, "create_proposal", "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .default(RIProposalVersion.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .default(RIProposalVersion.content_type, "comments", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .default(RICommentVersion.content_type, "", "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                });
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
