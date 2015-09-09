import AdhAbuseModule = require("../Abuse/Module");
import AdhCommentModule = require("../Comment/Module");
import AdhDocumentModule = require("../Document/Module");
import AdhHttpModule = require("../Http/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhProcessModule = require("../Process/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhProcess = require("../Process/Process");

import RIDigitalLebenProcess = require("../../Resources_/adhocracy_spd/resources/digital_leben/IProcess");

import SpdWorkbench = require("./spdWorkbench");


export var moduleName = "adhSPDWorkbench";

export var register = (angular) => {
    var processType = RIDigitalLebenProcess.content_type;

    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhDocumentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-spd-workbench></adh-spd-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", SpdWorkbench.registerRoutes(processType)])
        .directive("adhSpdWorkbench", ["adhConfig", "adhTopLevelState", SpdWorkbench.spdWorkbenchDirective])
        .directive("adhDocumentDetailColumn", ["adhConfig", "adhPermissions", SpdWorkbench.documentDetailColumnDirective])
        .directive("adhDocumentCreateColumn", ["adhConfig", SpdWorkbench.documentCreateColumnDirective])
        .directive("adhDocumentEditColumn", ["adhConfig", SpdWorkbench.documentEditColumnDirective])
        .directive("adhSpdProcessDetailColumn", ["adhConfig", "adhPermissions", SpdWorkbench.processDetailColumnDirective])
        .directive("adhSpdProcessDetailAnnounceColumn", ["adhConfig", SpdWorkbench.processDetailAnnounceColumnDirective]);
};
