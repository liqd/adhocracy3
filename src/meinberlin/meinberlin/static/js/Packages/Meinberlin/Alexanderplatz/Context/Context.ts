/// <reference path="../../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../../../Config/Config";

var pkgLocation = "/Meinberlin/Alexanderplatz/Context";


export var areaTemplate = (
    adhConfig: AdhConfig.IService,
    $templateRequest: angular.ITemplateRequestService
) => {
    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
};
