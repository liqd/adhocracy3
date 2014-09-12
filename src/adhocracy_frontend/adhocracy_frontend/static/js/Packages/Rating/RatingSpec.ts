/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhRating = require("./Rating");


export var register = () => {
    describe("Rating", () => {
        describe("Controller", () => {
            var adapterMock = <any>null;
            var scopeMock = <any>null;
            var qMock = <any>null;
            var httpMock = <any>null;
            var userMock = <any>null;
            var controller;

            var rateableResource;

            beforeEach(() => {
                scopeMock = {
                    postPoolSheet: "rateable",
                    postPoolField: "post_pool"
                };
                httpMock = { get: () => null };

                rateableResource = {
                    data: {
                        rateable: {
                            post_pool: "finish"
                        }
                    }
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
                        expect(path).toBe("finish");
                        done();
                    },
                    (msg) => {
                        expect(msg).toBe(false);
                        done();
                    }
                );
            });

            xit("updateRatings calculates the right totals for pro, contra, neutral and stores them in the scope.", () => {
                spyOn(httpMock, "get").and.returnValue(q.when(rateableResource));

                expect(true).toBe(false);
            });

            xit("does not throw an exception when initialized properly.", (done) => {
                controller = AdhRating.ratingController(
                    adapterMock,
                    scopeMock,
                    qMock,
                    httpMock,
                    userMock
                );

                controller.then(
                    () => { done(); },
                    (msg) => { expect(msg.toString()).toBe(false); done(); }
                );
            });
        });
    });
};
