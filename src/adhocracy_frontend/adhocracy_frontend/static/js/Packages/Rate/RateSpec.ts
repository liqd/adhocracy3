/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

// import RIRate = require("../../Resources_/adhocracy/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy/resources/rate/IRateVersion");
import SIRate = require("../../Resources_/adhocracy/sheets/rate/IRate");
import AdhRate = require("./Rate");
import AdhRateAdapter = require("./Adapter");
import PreliminaryNames = require ("../PreliminaryNames/PreliminaryNames");


export var register = () => {
    describe("Rate", () => {
        describe("Adapter", () => {
            var adapter : AdhRateAdapter.RateAdapter;
            var rateVersion : RIRateVersion;

            beforeEach(() => {
                adapter = new AdhRateAdapter.RateAdapter();
                rateVersion = new RIRateVersion({ preliminaryNames: new PreliminaryNames() });
                rateVersion.data["adhocracy.sheets.rate.IRate"] = new SIRate.AdhocracySheetsRateIRate({
                    subject: "sub",
                    object: "obj",
                    rate: 1
                });
            });

            it("rate returns rate correctly", () => {
                debugger;
                expect(adapter.rate(rateVersion)).toEqual(1);
            });

            it("rate sets rate correctly", () => {
                adapter.rate(rateVersion, -1);
                expect(rateVersion.data["adhocracy.sheets.rate.IRate"].rate).toEqual(-1);
            });
        });

        describe("Controller", () => {
            var scopeMock;
            var httpMock;
            var userMock;

            var rateableResource;
            var postPoolResource;
            var rateResources;

            beforeEach(() => {
                scopeMock = {
                    postPoolSheet: "rateable",
                    postPoolField: "post_pool",
                    refersTo: "comment_or_something"
                };

                httpMock = {
                    get: () => null,
                    getNewestVersionPath: () => q.when(null)
                };

                rateResources = [
                    { path: "r1",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user1",
                              object: "comment_or_something",
                              rate: 1
                          }
                      }
                    },
                    { path: "r2",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user2",
                              object: "comment_or_something",
                              rate: 1
                          }
                      }
                    },
                    { path: "r3",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user3",
                              object: "comment_or_something",
                              rate: 0
                          }
                      }
                    },
                    { path: "r4",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user4",
                              object: "comment_or_something",
                              rate: -1
                          }
                      }
                    },
                    { path: "r5",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user3",
                              object: "something_irrelevant",
                              rate: -1
                          }
                      }
                    }
                ];

                postPoolResource = {
                    data : {
                        "adhocracy.sheets.pool.IPool": {
                            elements: rateResources.map((r) => r.path)
                        }
                    }
                };

                rateableResource = {
                    data: {
                        rateable: {
                            post_pool: "post_pool_path"
                        }
                    }
                };

                userMock = {
                    userPath: "user3"
                };
            });

            it("resetRates clears rates and user rate in scope.", () => {
                scopeMock.rates = {
                    pro: 1,
                    contra: 1,
                    neutral: 1
                };
                scopeMock.thisUsersRate = "notnull";

                AdhRate.resetRates(scopeMock);
                expect(scopeMock.rates.pro).toBe(0);
                expect(scopeMock.rates.contra).toBe(0);
                expect(scopeMock.rates.neutral).toBe(0);
                expect(scopeMock.thisUserRate).toBeUndefined();
            });

            it("postPoolPathPromise promises post pool path.", (done) => {
                spyOn(httpMock, "get").and.returnValue(q.when(rateableResource));

                AdhRate.postPoolPathPromise(scopeMock, httpMock).then(
                    (path) => {
                        expect(path).toBe("post_pool_path");
                        done();
                    },
                    (msg) => {
                        expect(msg).toBe(false);
                        done();
                    }
                );
            });

            it("updateRates calculates the right totals for pro, contra, neutral and stores them in the scope.", (done) => {
                scopeMock.rates = {
                    pro: 1,
                    contra: 1,
                    neutral: 1
                };
                scopeMock.thisUsersRate = "notnull";

                var httpResponseStack =
                    [rateableResource, postPoolResource]
                    .concat(rateResources)
                    .reverse();
                spyOn(httpMock, "get").and.callFake(() => q.when(httpResponseStack.pop()));

                var adapter = new AdhRateAdapter.RateAdapter();

                AdhRate.updateRates(adapter, scopeMock, q, httpMock, userMock).then(
                    () => {
                        expect(scopeMock.rates.pro).toBe(2);
                        expect(scopeMock.rates.contra).toBe(1);
                        expect(scopeMock.rates.neutral).toBe(1);
                        expect(scopeMock.thisUsersRate.data["adhocracy.sheets.rate.IRate"].subject).toBe(userMock.userPath);
                        done();
                    },
                    (msg) => {
                        expect(msg).toBe(false);
                        done();
                    }
                );
            });
        });
    });
};
