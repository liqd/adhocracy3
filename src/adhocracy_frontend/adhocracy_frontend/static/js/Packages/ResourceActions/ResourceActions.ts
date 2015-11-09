import * as AdhConfig from "../Config/Config";
import * as AdhMovingColumns from "../MovingColumns/MovingColumns";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUtil from "../Util/Util";

var pkgLocation = "/ResourceActions";

export var resourceActionsDirective = (
    adhPermissions : AdhPermissions.Service,
	adhConfig: AdhConfig.IService
) => {
    return {
        restrict: "E",
        scope: {
            resourcePath: "@",
        	createDocumentPath: "=?",
        	share: "=?",
        	delete: "=?",
            print: "=?",
        	report: "=?",
            cancel: "=?"
        },
		templateUrl: adhConfig.pkg_path + pkgLocation + "/ResourceActions.html",
        link: (scope, element) => {
            console.log(scope);
			adhPermissions.bindScope(scope, () => scope.path && AdhUtil.parentPath(scope.path), "proposalItemOptions");
        }
    };
};

export var reportActionDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"report();\">{{ \"TR__REPORT\" | translate }}</a>",
        require: "^adhMovingColumn",
        scope: {
            class: "@"
        },
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.report = () => {
                column.toggleOverlay("abuse");
            };
        }
    };
};

export var cancelActionDirective = (
        adhConfig : AdhConfig.IService,
        adhTopLevelState : AdhTopLevelState.Service,
        adhResourceUrl) => {
    return {
        restrict: "E",
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"cancel();\">{{ \"TR__CANCEL\" | translate }}</a>",
        scope: {
            resourcePath: "@",
            parentPath: "@",
            class: "@"
        },
        link: (scope, element, attrs) => {
            scope.cancel = () => {
                if (!scope.resourcePath) {
                    scope.resourcePath = adhTopLevelState.get("processUrl");
                }
                var path = scope.parentPath ? AdhUtil.parentPath(scope.resourcePath) : scope.resourcePath;
                var url = adhResourceUrl(path);
                adhTopLevelState.goToCameFrom(url);
            };
        }
    };
};
