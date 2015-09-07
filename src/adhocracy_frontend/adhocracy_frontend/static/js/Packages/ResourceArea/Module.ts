import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhProcessModule = require("../Process/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUtil = require("../Util/Util");

import AdhResourceArea = require("./ResourceArea");


export var moduleName = "adhResourceArea";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhProcessModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("r", ["adhResourceArea", (adhResourceArea : AdhResourceArea.Service) => adhResourceArea]);
        }])
        .provider("adhResourceArea", AdhResourceArea.Provider)
        .directive("adhResourceArea", ["adhResourceArea", "$compile", AdhResourceArea.directive])
        .filter("adhParentPath", () => AdhUtil.parentPath)
        .filter("adhResourceUrl", ["adhConfig", AdhResourceArea.resourceUrl]);
};
