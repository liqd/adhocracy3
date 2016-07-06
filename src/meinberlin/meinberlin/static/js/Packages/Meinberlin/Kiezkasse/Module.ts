import * as AdhEmbedModule from "../../Embed/Module";
import * as AdhProcessModule from "../../Process/Module";
import * as AdhResourceAreaModule from "../../ResourceArea/Module";

import * as AdhIdeaCollectionModule from "../../IdeaCollection/Module";

import * as AdhEmbed from "../../Embed/Embed";
import * as AdhProcess from "../../Process/Process";
import * as AdhResourceArea from "../../ResourceArea/ResourceArea";

import * as AdhIdeaCollection from "../../IdeaCollection/IdeaCollection";

import RIKiezkasseProcess from "../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess";


export var moduleName = "adhMeinberlinKiezkasse";

export var register = (angular) => {
    var processType = RIKiezkasseProcess.content_type;

    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhIdeaCollectionModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkasse", ["kiezkassen"]);
        }])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider : AdhResourceArea.Provider, adhConfig) => {
            var registerRoutes = AdhIdeaCollection.registerRoutesFactory(processType);
            registerRoutes(processType)(adhResourceAreaProvider);
            registerRoutes(processType, "kiezkasse")(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollection.pkgLocation + "/ProcessHeaderSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] =
                "<adh-idea-collection-workbench data-is-kiezkasse=\"true\"></adh-idea-collection-workbench>";
        }]);
};
