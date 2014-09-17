/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhRating = require("./Rating");
import AdhRatingAdapter = require("./Adapter");


export var register = () => {
    describe("Rating", () => {
        describe("Controller", () => {
            var scopeMock;
            var httpMock;
            var userMock;

            var rateableResource;
            var postPoolResource;
            var ratingResources;

            beforeEach(() => {
                scopeMock = {
                    postPoolSheet: "rateable",
                    postPoolField: "post_pool"
                };
                httpMock = { get: () => null };

                // FIXME: rating value is not visible in the meta api
                // yet.

                // FIXME: do we have to filter for target manually
                // here, or can we assume we only get matching targets
                // from our post pool?  right now in these tests we
                // ignore target entirely.

                // FIXME: when sending an aggregate request, we also
                // need to be able to extract the rating for the
                // matching user explicitly, possibly in a separate
                // request.  will that be implemented?

                ratingResources = [
                    { path: "r1",
                      data: {
                          "adhocracy.sheets.rating.IRating": {
                              subject: "user1",
                              value: AdhRating.RatingValue.pro
                          }
                      }
                    },
                    { path: "r2",
                      data: {
                          "adhocracy.sheets.rating.IRating": {
                              subject: "user2",
                              value: AdhRating.RatingValue.pro
                          }
                      }
                    },
                    { path: "r3",
                      data: {
                          "adhocracy.sheets.rating.IRating": {
                              subject: "user3",
                              value: AdhRating.RatingValue.neutral
                          }
                      }
                    },
                    { path: "r4",
                      data: {
                          "adhocracy.sheets.rating.IRating": {
                              subject: "user4",
                              value: AdhRating.RatingValue.contra
                          }
                      }
                    }
                ];

                postPoolResource = {
                    data : {
                        "adhocracy.sheets.pool.IPool": {
                            elements: ratingResources.map((r) => r.path)
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

            it("resetRatings clears ratings and user rating in scope.", () => {
                scopeMock.ratings = {
                    pro: 1,
                    contra: 1,
                    neutral: 1
                };
                scopeMock.thisUsersRating = "notnull";

                AdhRating.resetRatings(scopeMock);
                expect(scopeMock.ratings.pro).toBe(0);
                expect(scopeMock.ratings.contra).toBe(0);
                expect(scopeMock.ratings.neutral).toBe(0);
                expect(scopeMock.thisUserRating).toBeUndefined();
            });

            it("postPoolPathPromise promises post pool path.", (done) => {
                spyOn(httpMock, "get").and.returnValue(q.when(rateableResource));

                AdhRating.postPoolPathPromise(scopeMock, httpMock).then(
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

            it("updateRatings calculates the right totals for pro, contra, neutral and stores them in the scope.", (done) => {
                scopeMock.ratings = {
                    pro: 1,
                    contra: 1,
                    neutral: 1
                };
                scopeMock.thisUsersRating = "notnull";

                var httpResponseStack =
                    [rateableResource, postPoolResource]
                    .concat(ratingResources)
                    .reverse();
                spyOn(httpMock, "get").and.callFake(() => q.when(httpResponseStack.pop()));

                var adapter = new AdhRatingAdapter.RatingAdapter();

                AdhRating.updateRatings(adapter, scopeMock, q, httpMock, userMock).then(
                    () => {
                        expect(scopeMock.ratings.pro).toBe(2);
                        expect(scopeMock.ratings.contra).toBe(1);
                        expect(scopeMock.ratings.neutral).toBe(1);
                        expect(scopeMock.thisUsersRating.data["adhocracy.sheets.rating.IRating"].subject).toBe(userMock.userPath);
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
