import * as AdhHttpModule from "../Http/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhImage from "./Image";


export var moduleName = "adhImage";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelStateModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .factory("adhUploadImage", ["adhHttp", AdhImage.uploadImageFactory])
        .directive("adhUploadImage", ["adhConfig", "adhHttp", "adhTopLevelState", "adhUploadImage",
            "flowFactory", "adhResourceUrlFilter", AdhImage.uploadImageDirective])
        .directive("adhShowImage", ["adhHttp", AdhImage.showImageDirective])
        .directive("adhBackgroundImage", ["adhHttp", AdhImage.backgroundImageDirective]);
};
