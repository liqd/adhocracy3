import * as AdhConfig from "../../Config/Config";

var pkgLocation = "/Pcompass/Context";


export var headerDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Header.html"
    };

};


export var areaTemplate = (
    adhConfig : AdhConfig.IService,
    $templateRequest : angular.ITemplateRequestService
) => {
    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/Template.html");
};
