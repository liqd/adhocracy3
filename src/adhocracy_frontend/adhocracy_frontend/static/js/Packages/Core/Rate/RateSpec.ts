/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as q from "q";

import * as AdhRate from "./Rate";

export var register = () => {
    describe("Rate", () => {
        var httpMock;
        var scopeMock;
        var userMock;

        describe("directive", () => {
            var directive;
            var adhConfigMock;
            var adhPermissionsMock;
            var adhPreliminaryNamesMock;
            var adhResourceAreaMock;
            var adhRateEventManagerMock;
            var adhRateService;
            var adhUserMock;

            beforeEach((done) => {
                adhPermissionsMock = jasmine.createSpyObj("adhPermissionsMock", ["bindScope"]);
                adhRateEventManagerMock = jasmine.createSpyObj("adhRateEventManagerMock", ["on", "off", "trigger"]);
                adhRateService = new AdhRate.Service(<any>q, httpMock);
                adhResourceAreaMock = jasmine.createSpyObj("adhResourceAreaMock", ["getProcess"]);

                adhConfigMock = <any>{};

                // only used in untested functions
                adhPreliminaryNamesMock = undefined;

                directive = AdhRate.directiveFactory("", "adhocracy_core.sheets.rate.IExample")(
                    <any>q,
                    adhRateService,
                    adhRateEventManagerMock,
                    adhConfigMock,
                    httpMock,
                    null,
                    adhPermissionsMock,
                    userMock,
                    adhPreliminaryNamesMock,
                    null,
                    adhResourceAreaMock,
                    adhUserMock,
                    done);

                directive.link(scopeMock);
            });

            xit("sets scope.ready when finished initializing", () => {
                expect(scopeMock.ready).toBe(true);
            });
        });
    });
};
