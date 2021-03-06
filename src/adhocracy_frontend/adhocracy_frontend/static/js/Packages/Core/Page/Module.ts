import * as AdhHttpModule from "../Http/Module";
import * as AdhMarkdownModule from "../Markdown/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as Page from "./Page";

export var moduleName = "adhPage";


export var register = (angular) => {
    angular.module(moduleName, [
        AdhHttpModule.moduleName,
        AdhMarkdownModule.moduleName,
        AdhResourceAreaModule.moduleName,
        AdhTopLevelStateModule.moduleName,
    ])
    .config(["adhResourceAreaProvider", Page.registerRoutes()])
    .directive("adhPage", ["adhConfig", "adhHttp", "adhTopLevelState", Page.pageDirective]);
};
