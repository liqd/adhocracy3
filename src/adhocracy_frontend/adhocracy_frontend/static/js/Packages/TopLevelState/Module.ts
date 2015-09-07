import AdhCredentialsModule = require("../User/Module");
import AdhEventManagerModule = require("../EventManager/Module");
import AdhTrackingModule = require("../Tracking/Module");

import AdhTopLevelState = require("./TopLevelState");


export var moduleName = "adhTopLevelState";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhCredentialsModule.moduleName,
            AdhEventManagerModule.moduleName,
            AdhTrackingModule.moduleName
        ])
        .provider("adhTopLevelState", AdhTopLevelState.Provider)
        .directive("adhPageWrapper", ["adhConfig", AdhTopLevelState.pageWrapperDirective])
        .directive("adhRoutingError", ["adhConfig", AdhTopLevelState.routingErrorDirective])
        .directive("adhSpace", ["adhTopLevelState", AdhTopLevelState.spaceDirective])
        .directive("adhSpaceSwitch", ["adhTopLevelState", "adhConfig", AdhTopLevelState.spaceSwitch])
        .directive("adhView", ["adhTopLevelState", "$compile", AdhTopLevelState.viewFactory]);
};
