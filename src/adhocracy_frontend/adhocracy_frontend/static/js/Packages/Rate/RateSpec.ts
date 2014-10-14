/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import RIRateVersion = require("../../Resources_/adhocracy_core/resources/rate/IRateVersion");
import SIRate = require("../../Resources_/adhocracy_core/sheets/rate/IRate");
import AdhRate = require("./Rate");
import AdhRateAdapter = require("./Adapter");
import PreliminaryNames = require ("../PreliminaryNames/PreliminaryNames");


var mkScopeMock = () => {
    return {
        postPoolPath: "post_pool_path",
        refersTo: "comment_or_something",
        rates: {
            pro: 1,
            contra: 1,
            neutral: 1
        },
        myRateResource: "notnull"
    };
};

var mkHttpMock = () => {
    return {
        get: () => q.when(),
        getNewestVersionPathNoFork: () => q.when()
    };
};

var mkRateResources = () => {
    return [
        {
            content_type: "adhocracy_core.resources.rate.IRateVersion",
            path: "r1",
            data: {
                "adhocracy_core.sheets.rate.IRate": {
                    subject: "user1",
                    object: "comment_or_something",
                    rate: 1
                }
            }
        },
        {
            content_type: "adhocracy_core.resources.rate.IRateVersion",
            path: "r2",
            data: {
                "adhocracy_core.sheets.rate.IRate": {
                    subject: "user2",
                    object: "comment_or_something",
                    rate: 1
                }
            }
        },
        {
            content_type: "adhocracy_core.resources.rate.IRateVersion",
            path: "r3",
            data: {
                "adhocracy_core.sheets.rate.IRate": {
                    subject: "user3",
                    object: "comment_or_something",
                    rate: 0
                }
            }
        },
        {
            content_type: "adhocracy_core.resources.rate.IRateVersion",
            path: "r4",
            data: {
                "adhocracy_core.sheets.rate.IRate": {
                    subject: "user4",
                    object: "comment_or_something",
                    rate: -1
                }
            }
        },
        {
            content_type: "adhocracy_core.resources.rate.IRateVersion",
            path: "r5",
            data: {
                "adhocracy_core.sheets.rate.IRate": {
                    subject: "user3",
                    object: "something_irrelevant",
                    rate: -1
                }
            }
        }
    ];
};

var mkPostPoolResource = (rateResources) => {
    return {
        data: {
            "adhocracy_core.sheets.pool.IPool": {
                elements: rateResources.map((r) => r.path)
            }
        }
    };
};

var mkRateableResource = () => {
    return {
        data: {
            "adhocracy_core.sheets.rate.IRateable": {
                post_pool: "post_pool_path"
            }
        }
    };
};

var mkUserMock = () => {
    return {
        userPath: "user3"
    };
};

export var register = () => {
    describe("Rate", () => {
        var httpMock;
        var rateResources;
        var postPoolResource;
        var rateableResource;
        var scopeMock;
        var userMock;

        describe("Adapter", () => {
            var adapter : AdhRateAdapter.RateAdapter;
            var rateVersion : RIRateVersion;

            beforeEach(() => {
                httpMock = mkHttpMock();
                rateResources = mkRateResources();
                postPoolResource = mkPostPoolResource(rateResources);
                rateableResource = mkRateableResource();
                scopeMock = mkScopeMock();
                userMock = mkUserMock();

                adapter = new AdhRateAdapter.RateAdapter();
                rateVersion = new RIRateVersion({ preliminaryNames: new PreliminaryNames() });
                rateVersion.data["adhocracy_core.sheets.rate.IRate"] = new SIRate.Sheet({
                    subject: "sub",
                    object: "obj",
                    rate: 1
                });
            });

            it("rate returns rate correctly", () => {
                expect(adapter.rate(rateVersion)).toEqual(1);
            });

            it("rate sets rate correctly", () => {
                adapter.rate(rateVersion, -1);
                expect(rateVersion.data["adhocracy_core.sheets.rate.IRate"].rate).toEqual(-1);
            });
        });

        describe("resetRates", () => {
            beforeEach(() => {
                httpMock = mkHttpMock();
                rateResources = mkRateResources();
                postPoolResource = mkPostPoolResource(rateResources);
                rateableResource = mkRateableResource();
                scopeMock = mkScopeMock();
                userMock = mkUserMock();
            });

            it("clears rates and user rate in scope.", () => {
                scopeMock.rates = {
                    pro: 1,
                    contra: 1,
                    neutral: 1
                };
                scopeMock.myRateResource = "notnull";

                AdhRate.resetRates(scopeMock);
                expect(scopeMock.rates.pro).toBe(0);
                expect(scopeMock.rates.contra).toBe(0);
                expect(scopeMock.rates.neutral).toBe(0);
                expect(scopeMock.thisUserRate).toBeUndefined();
            });
        });

        describe("updateRates", () => {
            var adapter : AdhRateAdapter.RateAdapter;

            beforeEach(() => {
                httpMock = mkHttpMock();
                rateResources = mkRateResources();
                postPoolResource = mkPostPoolResource(rateResources);
                rateableResource = mkRateableResource();
                scopeMock = mkScopeMock();
                userMock = mkUserMock();

                // http must be more accurately mocked for these tests.
                var httpMockResponder = (path, params) => {
                    if (typeof path === "undefined") {
                        throw "get request with undefined path.";
                    }

                    if (path === "post_pool_path") {
                        if (params["content_type"] === RIRateVersion.content_type) {
                            var result = _.cloneDeep(rateResources);
                            if (params[SIRate.nick + ":subject"] === "user3") {
                                result = result.filter((resource) =>
                                                       resource.data["adhocracy_core.sheets.rate.IRate"].subject === "user3");
                            }
                            if (params[SIRate.nick + ":subject"] === "user3") {
                                result = result.filter((resource) =>
                                                       resource.data["adhocracy_core.sheets.rate.IRate"].subject === "user3");
                            }

                            // ...

                            // FIXME: result must not be an array, but
                            // a pool object that contains the array
                            // as elements.  this is getting really
                            // complicated...

                            return q.when(result);
                        }
                    }
                };
                spyOn(httpMock, "get").and.callFake(httpMockResponder);

                adapter = new AdhRateAdapter.RateAdapter();
            });

            it("calculates the right totals for pro, contra, neutral and stores them in the scope.", (done) => {
                AdhRate.fetchAggregatedRates(adapter, scopeMock, q, httpMock, userMock).then(
                    () => {
                        expect(scopeMock.rates.pro).toBe(2);
                        expect(scopeMock.rates.contra).toBe(1);
                        expect(scopeMock.rates.neutral).toBe(1);
                        expect(scopeMock.myRateResource.data["adhocracy_core.sheets.rate.IRate"].subject).toBe(userMock.userPath);
                        done();
                    },
                    (msg) => {
                        expect(msg).toBe(false);
                        done();
                    }
                );
            });
        });

        describe("rateController", () => {
            var adapterMock;
            var adhPermissionsMock;
            var adhPreliminaryNamesMock;
            var realFetchAggregatedRates;
            var realFetchAuditTrail;

            beforeEach((done) => {
                adapterMock = jasmine.createSpyObj("adapterMock", ["subject", "object", "rate", "rateablePostPoolPath"]);
                adhPermissionsMock = jasmine.createSpyObj("adhPermissionsMock", ["bindScope"]);

                realFetchAggregatedRates = AdhRate.fetchAggregatedRates;
                spyOn(AdhRate, "fetchAggregatedRates").and.returnValue(q.when());

                realFetchAuditTrail = AdhRate.fetchAuditTrail;
                spyOn(AdhRate, "fetchAuditTrail").and.returnValue(q.when());

                realFetchAggregatedRates = undefined;
                realFetchAuditTrail = undefined;

                // only used in untested functions
                adhPreliminaryNamesMock = undefined;

                // FIXME: $httpMock does not give the right answers.
                // in particular, it responds with 'undefined' to the
                // request for the rateable in fetchPostPoolPath.
                //
                // AdhRate.rateController(adapterMock, scopeMock, q, httpMock, adhPermissionsMock, userMock, adhPreliminaryNamesMock)
                //     .then(done, (reason) => {
                //         expect(reason).toBe(undefined);
                //     });
            });

            afterEach(() => {
                AdhRate.fetchAggregatedRates = realFetchAggregatedRates;
                AdhRate.fetchAuditTrail = realFetchAuditTrail;
            });

            xit("sets scope.ready when finished initializing", () => {
                expect(scopeMock.ready).toBe(true);
            });
        });
    });
};
