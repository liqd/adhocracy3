/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import modernizr = require("modernizr");

// import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhMetaApi = require("../MetaApi/MetaApi");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
// import AdhResource = require("../../Resources");
import AdhUser = require("../User/User");
// import ResourcesBase = require("../../ResourcesBase");
// import Resources = require("../../Resources");
import RIComment = require("../../Resources_/adhocracy_core/resources/comment/IComment");
import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIProposal = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposal");
import RIProposalVersion = require("../../Resources_/adhocracy_core/resources/sample_proposal/IProposalVersion");
import RIRate = require("../../Resources_/adhocracy_core/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy_core/resources/rate/IRateVersion");
import RISection = require("../../Resources_/adhocracy_core/resources/sample_section/ISection");
import RISectionVersion = require("../../Resources_/adhocracy_core/resources/sample_section/ISectionVersion");
// import RITag = require("../../Resources_/adhocracy_core/interfaces/ITag");
import SICommentable = require("../../Resources_/adhocracy_core/sheets/comment/ICommentable");
import SIComment = require("../../Resources_/adhocracy_core/sheets/comment/IComment");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");
import SIRate = require("../../Resources_/adhocracy_core/sheets/rate/IRate");
// import SIUserBasic = require("../../Resources_/adhocracy_core/sheets/user/IUserBasic");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");


export var register = (angular, config, meta_api) => {

    // Sine initialization is async, we need to call it through
    // beforeEach.  Since we only want to call it once, we wrap this
    // dummy "describe" around the entire test suite.

    describe("[]", () => {
        var adhMetaApi : AdhMetaApi.MetaApiQuery;
        var adhPreliminaryNames : AdhPreliminaryNames;
        var adhHttp : AdhHttp.Service<any>;
        var adhUser : AdhUser.User;

        var _proposalVersion : RIProposalVersion;
        var _commentVersion : RICommentVersion;
        var _rateVersion : RIRateVersion;

        beforeEach((done) => {
            adhMetaApi = angular.injector(["ng"]).invoke(() => new AdhMetaApi.MetaApiQuery(meta_api));
            adhPreliminaryNames = angular.injector(["ng"]).invoke(() => new AdhPreliminaryNames());

            adhHttp = (() => {
                var factory = ($http, $q, $timeout) => {
                    return (new AdhHttp.Service($http, $q, $timeout, adhMetaApi, adhPreliminaryNames, config));
                };
                factory.$inject = ["$http", "$q", "$timeout"];
                return angular.injector(["ng"]).invoke(factory);
            })();

            adhUser = (() => {
                var factory = (
                    $q,
                    $http,
                    $rootScope,
                    $window
                ) => {
                    return (new AdhUser.User(
                        adhHttp,
                        $q,
                        $http,
                        $rootScope,
                        $window,
                        angular,
                        modernizr
                    ));
                };
                factory.$inject = ["$q", "$http", "$rootScope", "$window"];
                return angular.injector(["ng"]).invoke(factory);
            })();

            var poolPath = "/adhocracy";
            var proposalName = "Against_Curtains_" + Math.random();
                // (we don't have a way yet to repeat this test
                // without having to come up with new names every
                // time, so we just randomise.)

            var cb = (transaction : any) : ng.IPromise<void> => {
                // post items
                var proposal : AdhHttp.ITransactionResult =
                    transaction.post(poolPath, new RIProposal({preliminaryNames: adhPreliminaryNames, name: proposalName}));
                var section : AdhHttp.ITransactionResult =
                    transaction.post(proposal.path, new RISection({preliminaryNames: adhPreliminaryNames, name : "motivation"}));
                var comment : AdhHttp.ITransactionResult =
                    transaction.post(proposal.path, new RIComment({preliminaryNames: adhPreliminaryNames, name : "comment"}));

                // post section version
                var sectionVersionResource = new RISectionVersion({preliminaryNames: adhPreliminaryNames});
                var sectionVersion : AdhHttp.ITransactionResult = transaction.post(section.path, sectionVersionResource);

                // post proposal version
                var proposalVersionResource = new RIProposalVersion({preliminaryNames: adhPreliminaryNames});
                proposalVersionResource.data["adhocracy_core.sheets.document.IDocument"] =
                    new SIDocument.AdhocracyCoreSheetsDocumentIDocument({
                        title: proposalName,
                        description: "whoof",
                        elements: [sectionVersion.path]
                    });
                proposalVersionResource.data["adhocracy_core.sheets.versions.IVersionable"] =
                    new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({
                        follows: [proposal.first_version_path]
                    });
                var proposalVersion : AdhHttp.ITransactionResult = transaction.post(proposal.path, proposalVersionResource);

                // post comment version
                var commentVersionResource = new RICommentVersion({preliminaryNames: adhPreliminaryNames});
                commentVersionResource.data[SIComment.nick] = new SIComment.AdhocracyCoreSheetsCommentIComment({
                    refers_to: proposalVersion.path,
                    content: "this is my two cents"
                });
                var commentVersion : AdhHttp.ITransactionResult = transaction.post(comment.path, commentVersionResource);

                // post rate item
                var rate : AdhHttp.ITransactionResult =
                    transaction.post(comment.path, new RIRate({preliminaryNames: adhPreliminaryNames, name : "rate"}));

                // post rate version
                var rateVersionResource = new RIRateVersion({preliminaryNames: adhPreliminaryNames});
                rateVersionResource.data[SIRate.nick] = new SIRate.AdhocracyCoreSheetsRateIRate({
                    subject: adhUser.userPath,
                    object: commentVersion.path,
                    rate: 1
                });
                rateVersionResource.data[SIVersionable.nick] = new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({
                    follows: [rate.first_version_path]
                });
                var rateVersion : AdhHttp.ITransactionResult = transaction.post(rate.path, rateVersionResource);

                var proposalVersionProper = transaction.get(proposalVersion.path);
                var commentVersionProper = transaction.get(commentVersion.path);
                var rateVersionProper = transaction.get(rateVersion.path);

                // commit everything
                return transaction.commit()
                    .then(
                        (responses) : void => {
                            _proposalVersion = responses[proposalVersionProper.index];
                            _commentVersion = responses[commentVersionProper.index];
                            _rateVersion = responses[rateVersionProper.index];
                            done();
                        },
                        (error) : void => {
                            console.log("*** ERROR: " + error);
                            done();
                        });
            };

            adhHttp.withTransaction(cb);
        });

        describe("filter pools", () => {
            it("sets up fixtures properly", () => {
                expect(_proposalVersion.content_type).toEqual(RIProposalVersion.content_type);
                expect(_commentVersion.content_type).toEqual(RICommentVersion.content_type);
                expect(_rateVersion.content_type).toEqual(RIRateVersion.content_type);
            });

            it("logs in god", () => {
                expect(adhUser.userPath).toContain("/principals/users/0000000/");
            });

            it("/adhocracy is postable", (done) => {
                adhHttp.options("/adhocracy")
                    .then((options) => {
                        expect(options.POST).toBe(true);
                        done();
                    })
            });

            it("query 1: user's own rating", (done) => {
                var ratePostPoolPath = _commentVersion.data[SICommentable.nick].post_pool;

                var query : any = {};
                query.content_type = RIRateVersion.content_type;
                query.depth = 2;
                query.tag = "LAST";
                query[SIRate.nick + ":subject"] = adhUser.userPath;

                adhHttp.get(ratePostPoolPath, query)
                    .then(
                        (poolRsp) => {
                            var elements : string[] = poolRsp.data[SIPool.nick].elements;
                            expect(elements.length).toEqual(1);
                            adhHttp.get(elements[0])
                                .then((rateRsp) => {
                                    expect(rateRsp.content_type).toEqual(RIRateVersion.content_type);
                                    done();
                                });
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        });
            });

            it("query 2: rating totals", (done) => {
                var ratePostPoolPath = _commentVersion.data[SICommentable.nick].post_pool;

                var aggrkey : string = "rate";
                var query : any = {};
                query.content_type = RIRateVersion.content_type;
                query.depth = 2;
                query.tag = "LAST";
                query.count = "true";
                query.aggregateby = aggrkey;

                adhHttp.get(ratePostPoolPath, query)
                    .then(
                        (poolRsp) => {
                            var rspCounts = poolRsp.data[SIPool.nick].aggregateby;
                            expect(rspCounts.hasOwnProperty(aggrkey)).toBe(true);
                            expect(rspCounts[aggrkey]).toEqual({"1": 1});  // 0-counts are omitted
                            done();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                            done();
                        });
            });
        });
    });
};
