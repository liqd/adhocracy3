import AdhResourceArea = require("../../../ResourceArea/ResourceArea");

import RIAlexanderplatzProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess");
import RIDocument = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IDocument");
import RIDocumentVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IDocumentVersion");
import RIParagraph = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import RIProposal = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProposal");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProposalVersion");


export var moduleName = "adhMeinBerlinAlexanderplatzWorkbench";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhResourceArea.moduleName
        ])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                // documents tab
                .default(RIAlexanderplatzProcess, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "documents"
                })
                .default(RIAlexanderplatzProcess, "create_document", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "documents"
                })
                .defaultVersionable(RIDocument, RIDocumentVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "documents"
                })
                .defaultVersionable(RIParagraph, RIParagraphVersion, "comments", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show",
                    tab: "documents"
                })

                // proposals tab
                .default(RIAlexanderplatzProcess, "proposals", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "proposals"
                })
                .default(RIAlexanderplatzProcess, "create_proposal", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "proposals"
                })
                .defaultVersionable(RIProposal, RIProposalVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "proposals"
                })
                .defaultVersionable(RIProposal, RIProposalVersion, "comments", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show",
                    tab: "proposals"
                });
        }]);
};
