import * as AdhShareSocialModule from "../ShareSocial/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhMovingColumns from "./MovingColumns";


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
