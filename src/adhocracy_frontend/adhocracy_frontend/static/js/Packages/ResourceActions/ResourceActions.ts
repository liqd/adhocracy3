import * as AdhConfig from "../Config/Config";
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
            cancel: "=?"
        },
		templateUrl: adhConfig.pkg_path + pkgLocation + "/ResourceActions.html",
        link: (scope, element) => {
			adhPermissions.bindScope(scope, () => scope.path && AdhUtil.parentPath(scope.path), "proposalItemOptions");
        }
    };
};

export var cancelDirective = (
        adhConfig : AdhConfig.IService,
        adhTopLevelState : AdhTopLevelState.Service,
        adhResourceUrl) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Cancel.html",
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
