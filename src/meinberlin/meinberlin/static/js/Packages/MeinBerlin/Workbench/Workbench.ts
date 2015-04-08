import AdhConfig = require("../../Config/Config");
import AdhMovingColumns = require("../../MovingColumns/MovingColumns");
import AdhResourceArea = require("../../ResourceArea/ResourceArea");

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
            AdhResourceArea.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            // FIXME
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
