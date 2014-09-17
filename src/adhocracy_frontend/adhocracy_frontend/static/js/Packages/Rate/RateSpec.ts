/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhRate = require("./Rate");
import AdhRateAdapter = require("./Adapter");


export var register = () => {
    describe("Rate", () => {
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
                    postPoolField: "post_pool"
                };
                httpMock = { get: () => null };

                rateResources = [
                    { path: "r1",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user1",
                              value: AdhRate.RateValue.pro
                          }
                      }
                    },
                    { path: "r2",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user2",
                              value: AdhRate.RateValue.pro
                          }
                      }
                    },
                    { path: "r3",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user3",
                              value: AdhRate.RateValue.neutral
                          }
                      }
                    },
                    { path: "r4",
                      data: {
                          "adhocracy.sheets.rate.IRate": {
                              subject: "user4",
                              value: AdhRate.RateValue.contra
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
