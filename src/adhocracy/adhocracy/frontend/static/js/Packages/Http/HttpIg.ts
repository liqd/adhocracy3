/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import Resources = require("../../Resources");
import RIProposal = require("../../Resources_/adhocracy_sample/resources/proposal/IProposal");
import RIProposalVersion = require("../../Resources_/adhocracy_sample/resources/proposal/IProposalVersion");
import RISection = require("../../Resources_/adhocracy_sample/resources/section/ISection");
import RISectionVersion = require("../../Resources_/adhocracy_sample/resources/section/ISectionVersion");
import RITag = require("../../Resources_/adhocracy/interfaces/ITag");
import AdhMetaApi = require("../MetaApi/MetaApi");
import AdhHttp = require("./Http");


export var register = (angular, config, meta_api) => {

    describe("withTransaction", () => {
        var adhHttp : AdhHttp.Service<any> = (() => {
            var factory = ($http, $q) => {
                return (new AdhHttp.Service($http, $q, new AdhMetaApi.MetaApiQuery(meta_api)));
            };
            factory.$inject = ["$http", "$q"];
            return angular.injector(["ng"]).invoke(factory);
        })();

        beforeEach(() => {
            return;
        });

        it("Deep-rewrites preliminary resource paths.", (done) => {
            var poolPath = "/adhocracy";
            var proposalName = "Against Curtains " + Math.random();
                // (we don't have a way yet to repeat this test
                // without having to come up with new names every
                // time, so we just randomise.)

            var cb = (transaction : any) : ng.IPromise<void> => {
                var proposal : AdhHttp.ITransactionResult = transaction.post(poolPath, new RIProposal(proposalName));
                var section : AdhHttp.ITransactionResult = transaction.post(proposal.path, new RISection("Motivation"));

                var sectionVersionResource = new RISectionVersion();
                var sectionVersion : AdhHttp.ITransactionResult = transaction.post(section.path, sectionVersionResource);

                var proposalVersionResource = new RIProposalVersion();
                proposalVersionResource.data["adhocracy.sheets.document.IDocument"] = {
                    title: proposalName,
                    description: "whoof",
                    elements: [sectionVersion.path]
                };
                proposalVersionResource.data["adhocracy.sheets.document.IVersionable"] = {
                    follows: [proposal.first_version_path]
                };
                var proposalVersion : AdhHttp.ITransactionResult =
                    transaction.post(proposal.path, proposalVersion);

                return transaction.commit()
                    .then((responses) : ng.IPromise<Resources.Content<any>> => {
                        var lastTagPath : string = responses[proposalVersion.index].path + "/LAST";
                        return adhHttp.get(lastTagPath);
                    })
                    .then((lastTag : RITag) => {
                        var lastVersionPaths : string[] = lastTag.data["adhocracy.sheets.tags.ITag"].elements;
                        expect(lastVersionPaths.length).toBe(1);
                        expect(lastVersionPaths[0].substring(lastVersionPaths[0].length - 4)).toBe("0001");
                        done();
                    });
            };

            adhHttp.withTransaction(cb);
        });

        xit("Keeps track of the LAST tag properly.", (done) => {
            expect(false).toBe(true);
            done();
        });
    });
};
