import * as AdhHttpModule from "../Http/Module";

import * as Activity from "./Activity";


export var moduleName = "adhActivity";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName
        ])
        .directive("adhActivityStream", ["adhConfig", "adhHttp", Activity.streamDirective])
        .directive("adhActivity", ["adhConfig", "adhHttp", Activity.activityDirective]);
};
