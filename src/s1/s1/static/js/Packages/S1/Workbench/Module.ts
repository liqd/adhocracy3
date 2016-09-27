import * as AdhCommentModule from "../../Core/Comment/Module";
import * as AdhHttpModule from "../../Core/Http/Module";
import * as AdhMarkdownModule from "../../Core/Markdown/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../Core/TopLevelState/Module";

import * as AdhProcess from "../../Core/Process/Process";

import RIS1Process from "../../../Resources_/adhocracy_s1/resources/s1/IProcess";

import * as Workbench from "./Workbench";


export var moduleName = "adhS1Workbench";

export var register = (angular) => {
    var processType = RIS1Process.content_type;

    angular
        .module(moduleName, [
            AdhCommentModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMarkdownModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (
            adhResourceAreaProvider,
            adhConfig
        ) => {
            var processHeaderSlot = adhConfig.pkg_path + Workbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
            Workbench.registerRoutes(processType)(adhResourceAreaProvider);
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[RIS1Process.content_type] = "<adh-s1-workbench></adh-s1-workbench>";
        }])
        .directive("adhS1Workbench", ["adhConfig", "adhTopLevelState", Workbench.s1WorkbenchDirective])
        .directive("adhS1Landing", ["adhConfig", "adhHttp", "adhTopLevelState", Workbench.s1LandingDirective])
        .directive("adhS1CurrentColumn", ["adhConfig", "adhHttp", "adhTopLevelState", Workbench.s1CurrentColumnDirective])
        .directive("adhS1NextColumn", ["adhConfig", "adhHttp", "adhTopLevelState", Workbench.s1NextColumnDirective])
        .directive("adhS1ArchiveColumn", ["adhConfig", "adhHttp", "adhTopLevelState", Workbench.s1ArchiveColumnDirective])
        .directive("adhS1ProposalDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", Workbench.s1ProposalDetailColumnDirective])
        .directive("adhS1ProposalCreateColumn", ["adhConfig", "adhTopLevelState", Workbench.s1ProposalCreateColumnDirective])
        .directive("adhS1ProposalEditColumn", ["adhConfig", "adhTopLevelState", Workbench.s1ProposalEditColumnDirective]);
};
