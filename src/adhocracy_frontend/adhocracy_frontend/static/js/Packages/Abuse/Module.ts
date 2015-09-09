import AdhHttpModule = require("../Http/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");

import AdhAbuse = require("./Abuse");


export var moduleName = "adhReportAbuse";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName
        ])
        .directive("adhReportAbuse", ["adhHttp", "adhConfig", AdhAbuse.reportAbuseDirective]);
};
