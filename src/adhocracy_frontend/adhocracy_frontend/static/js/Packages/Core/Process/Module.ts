import * as AdhHttpModule from "../Http/Module";
import * as AdhNamesModule from "../Names/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as Process from "./Process";


export var moduleName = "adhProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
            AdhNamesModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .provider("adhProcess", Process.Provider)
        .directive("adhWorkflowSwitch", [
            "adhConfig", "adhHttp", "adhPermissions", "$q", "$translate", "$window", Process.workflowSwitchDirective])
        .directive("adhProcessView", ["adhTopLevelState", "adhProcess", "$compile", Process.processViewDirective])
        .directive("adhProcessListItem", ["adhConfig", "adhHttp", "adhNames", Process.listItemDirective])
        .directive("adhProcessListing", ["adhConfig", Process.listingDirective])
        .directive("adhCurrentProcessTitle", ["adhTopLevelState", "adhHttp", Process.currentProcessTitleDirective])
        .directive("adhIdeaCollectionDetail", ["adhConfig", "adhEmbed", "adhHttp", "adhPermissions", "$q", Process.detailDirective]);
};
