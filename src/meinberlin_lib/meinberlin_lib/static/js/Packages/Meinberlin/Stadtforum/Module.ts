import * as AdhMeinberlinStadtforumProcessModule from "./Process/Module";
import * as AdhMeinberlinStadtforumProposalModule from "./Proposal/Module";
import * as AdhIdeaCollectionModule from "../../Core/IdeaCollection/Module";
import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";

import * as AdhIdeaCollectionWorkbench from "../../Core/IdeaCollection/Workbench/Workbench";
import * as AdhNames from "../../Core/Names/Names";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";

import RIPoll from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IPoll";
import RIProposalVersion from "../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";
import RIStadtforumProcess from "../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IProcess";

export var moduleName = "adhMeinberlinStadtforum";

export var register = (angular) => {
    AdhMeinberlinStadtforumProcessModule.register(angular);
    AdhMeinberlinStadtforumProposalModule.register(angular);
    var processType = RIStadtforumProcess.content_type;

    angular
        .module(moduleName, [
            AdhMeinberlinStadtforumProcessModule.moduleName,
            AdhMeinberlinStadtforumProposalModule.moduleName,
        ]);
            AdhIdeaCollectionModule.moduleName,
            AdhNamesModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var registerRoutes = AdhIdeaCollectionWorkbench.registerRoutesFactory(
                RIStadtforumProcess, RIPoll, RIProposalVersion);
            registerRoutes()(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollectionWorkbench.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", "adhConfig", (adhProcessProvider : AdhProcess.Provider, adhConfig) => {
            adhProcessProvider.templates[processType] =
                "<adh-idea-collection-workbench data-process-properties=\"processProperties\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.processProperties[processType] = {
                proposalClass: RIPoll,
                proposalVersionClass: RIProposalVersion
            };
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[processType] = "TR__RESOURCE_STADTFORUM";
            adhNamesProvider.names[RIProposalVersion.content_type] = "TR__RESOURCE_POLL";
        }]);
};
