import * as AdhConfig from "../Config/Config";

var pkgLocation = "/Home";


export var homeDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Home.html",
        scope: {}
    };
};
