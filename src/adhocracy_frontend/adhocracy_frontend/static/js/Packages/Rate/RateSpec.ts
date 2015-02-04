/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import q = require("q");

import AdhRate = require("./Rate");
import AdhRateAdapter = require("./Adapter");
import AdhPreliminaryNames = require ("../PreliminaryNames/PreliminaryNames");

import RIRateVersion = require("../../Resources_/adhocracy_core/resources/rate/IRateVersion");
import SIRate = require("../../Resources_/adhocracy_core/sheets/rate/IRate");

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
                rateVersion = new RIRateVersion({ preliminaryNames: new AdhPreliminaryNames.Service() });
                rateVersion.data["adhocracy_core.sheets.rate.IRate"] = new SIRate.Sheet({
                    subject: "sub",
                    object: "obj",
                    rate: <any>1
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

        describe("directive", () => {
            var directive;
            var adapterMock;
            var adhConfigMock;
            var adhPermissionsMock;
            var adhPreliminaryNamesMock;

            beforeEach((done) => {
                adapterMock = jasmine.createSpyObj("adapterMock", ["subject", "object", "rate", "rateablePostPoolPath"]);
                adhPermissionsMock = jasmine.createSpyObj("adhPermissionsMock", ["bindScope"]);

                adhConfigMock = <any>{};

                // only used in untested functions
                adhPreliminaryNamesMock = undefined;

                directive = AdhRate.directiveFactory("", adapterMock)(
                    <any>q,
                    adhConfigMock,
                    httpMock,
                    null,
                    adhPermissionsMock,
                    userMock,
                    adhPreliminaryNamesMock,
                    null,
                    done);

                directive.link(scopeMock);
            });

            xit("sets scope.ready when finished initializing", () => {
                expect(scopeMock.ready).toBe(true);
            });
        });
    });
};
