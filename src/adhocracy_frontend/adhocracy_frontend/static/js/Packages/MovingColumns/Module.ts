import AdhShareSocialModule = require("../ShareSocial/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhMovingColumns = require("./MovingColumns");


export var moduleName = "adhMovingColumns";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelStateModule.moduleName,
            AdhShareSocialModule.moduleName
        ])
        .directive("adhMovingColumn", ["adhConfig", AdhMovingColumns.movingColumnDirective])
        .directive("adhMovingColumns", ["adhTopLevelState", "$timeout", "$window", AdhMovingColumns.movingColumns]);
};
