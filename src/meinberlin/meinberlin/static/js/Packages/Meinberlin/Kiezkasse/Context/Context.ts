import * as AdhConfig from "../../../Config/Config";

var pkgLocation = "/Meinberlin/Kiezkasse/Context";


export var areaTemplate = (
    adhConfig : AdhConfig.IService,
    $templateRequest : angular.ITemplateRequestService
) => {
    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
};
