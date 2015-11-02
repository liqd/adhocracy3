import * as AdhConfig from "../Config/Config";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhUtil from "../Util/Util";

var pkgLocation = "/ResourceActions";

export var resourceActions = (
adhPermissions : AdhPermissions.Service,
	adhConfig: AdhConfig.IService
) => {
    return {
        restrict: "E",
        scope: {
        	path: "=",
        	editurl: "@",
        	reportfunction: "=?",
        	sharefunction: "=?",
        	deletefunction: "=?",
        	printfunction: "=?"

        },
		templateUrl: adhConfig.pkg_path + pkgLocation + "/ResourceActions.html",
        link: (scope, element) => {
			adhPermissions.bindScope(scope, () => scope.path && AdhUtil.parentPath(scope.path), "proposalItemOptions");
			console.log(scope);
        }
    };
};