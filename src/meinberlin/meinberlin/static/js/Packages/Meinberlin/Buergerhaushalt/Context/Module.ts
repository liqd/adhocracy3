import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhResourceAreaModule from "../../../ResourceArea/Module";

import * as AdhMeinberlinIdeaCollectionModule from "../../IdeaCollection/Module";

import * as AdhEmbed from "../../../Embed/Embed";
import * as AdhResourceArea from "../../../ResourceArea/ResourceArea";

import * as AdhMeinberlinIdeaCollection from "../../IdeaCollection/IdeaCollection";

import RIBuergerhaushaltProcess from "../../../../Resources_/adhocracy_meinberlin/resources/burgerhaushalt/IProcess";


export var moduleName = "adhMeinberlinBuergerhaushaltContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhMeinberlinIdeaCollectionModule.moduleName,
            AdhResourceAreaModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("buergerhaushalt", ["burgerhaushalt"]);
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            AdhMeinberlinIdeaCollection.registerRoutesFactory(RIBuergerhaushaltProcess.content_type)(
                RIBuergerhaushaltProcess.content_type,
                "buergerhaushalt"
            )(adhResourceAreaProvider);
        }]);
};
