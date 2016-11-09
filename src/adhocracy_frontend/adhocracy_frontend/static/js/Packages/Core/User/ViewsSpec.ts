/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as q from "q";

import * as AdhUserViews from "./Views";


export var register = () => {
    describe("UserViews", () => {
        var adhPermissionsMock;
        beforeEach(() => {
            adhPermissionsMock = {
                bindScope: jasmine.createSpy("adhPermissions.bindScope").and.returnValue("")
            };
        });

        describe("loginDirective", () => {
            var directive;
            var adhConfigMock;
            var adhUserMock;
            var adhTopLevelStateMock;
            var adhEmbedMock;

            beforeEach(() => {
                adhConfigMock = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true,
                    support_email: "support@adhocracy.com"
                };
                adhUserMock = jasmine.createSpyObj("adhUserMock", ["logIn"]);
                adhUserMock.logIn.and.returnValue(q.when(undefined));
                adhTopLevelStateMock = jasmine.createSpyObj("adhTopLevelStateMock", ["goToCameFrom"]);
                adhEmbedMock = jasmine.createSpyObj("adhEmbedMock", ["getContext"]);
                directive = AdhUserViews.loginDirective(
                    adhConfigMock, null, adhUserMock, adhTopLevelStateMock, adhEmbedMock, adhPermissionsMock, "adhShowError", null);
            });

            describe("link", () => {
                var scopeMock;

                beforeEach(() => {
                    scopeMock = {
                        loginForm: {
                            $setPristine: () => undefined
                        }
                    };
                    directive.link(scopeMock);
                });

                it("creates an empty credentials object in scope", () => {
                    expect(scopeMock.credentials).toEqual({nameOrEmail: "", password: ""});
                });

                describe("resetCredentials", () => {
                    it("cresets scope.credentials to empty strings", () => {
                        scopeMock.credentials.nameOrEmail = "foo";
                        scopeMock.credentials.password = "bar";

                        scopeMock.resetCredentials();

                        expect(scopeMock.credentials).toEqual({nameOrEmail: "", password: ""});
                    });
                });

                describe("logIn", () => {
                    beforeEach(() => {
                        scopeMock.credentials.nameOrEmail = "foo";
                        scopeMock.credentials.password = "bar";
                    });

                    it("calls adhUser.logIn with scope.nameOrEmail and scope.password", (done) => {
                        scopeMock.logIn().then(() => {
                            expect(adhUserMock.logIn).toHaveBeenCalledWith("foo", "bar");
                            done();
                        });
                    });
                    it("redirects to cameFrom or / if everything goes well", (done) => {
                        scopeMock.logIn().then(() => {
                            expect(adhTopLevelStateMock.goToCameFrom).toHaveBeenCalledWith("/", true);
                            done();
                        });
                    });
                    it("charges $scope.errors if something goes wrong", (done) => {
                        adhUserMock.logIn.and.returnValue(q.reject([{description: "error"}]));
                        scopeMock.logIn().then(() => {
                            expect(scopeMock.errors.length).toBe(1);
                            done();
                        });
                    });
                    it("resets password if something goes wrong", (done) => {
                        adhUserMock.logIn.and.returnValue(q.reject([{description: "error"}]));
                        scopeMock.logIn().then(() => {
                            expect(scopeMock.credentials.password).toBe("");
                            done();
                        });
                    });
                });
            });
        });

        describe("indicatorDirective", () => {
            var directive;
            var adhConfigMock;
            var adhResourceAreaMock;

            beforeEach(() => {
                adhConfigMock = {
                    pkg_path: "mock",
                    root_path: "mock",
                    ws_url: "mock",
                    embedded: true
                };
                adhResourceAreaMock = jasmine.createSpyObj("adhResourceArea", ["has"]);
                adhResourceAreaMock.has.and.returnValue(false);
                directive = AdhUserViews.indicatorDirective(adhConfigMock, adhResourceAreaMock, null, adhPermissionsMock, null);
            });

            describe("controller", () => {
                var controller;
                var scopeMock;
                var adhUserMock;

                beforeEach(() => {
                    scopeMock = {};
                    adhUserMock = jasmine.createSpyObj("adhUserMock", ["logOut"]);
                    controller = <any>(directive.controller[3]);
                    controller(adhUserMock, null, scopeMock);
                });

                describe("logOut", () => {
                    it("calls adhUser.logOut", () => {
                        scopeMock.logOut();
                        expect(adhUserMock.logOut).toHaveBeenCalled();
                    });
                });
            });
        });
    });
};
