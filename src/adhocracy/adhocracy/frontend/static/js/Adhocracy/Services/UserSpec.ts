/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

// FIXME: DefinitelyTyped is not yet compatible with jasmine 2.0.0
declare var beforeEach : (any) => void;

import AdhUser = require("./User");
import Util = require("../Util");
import q = require("q");

export var register = () => {
    describe("Service/User", () => {

        var adhUser;
        var adhHttpMock;
        var httpMock;
        var windowMock;
        var modernizrMock;

        describe("User", () => {
            beforeEach(() => {
                adhHttpMock = <any>jasmine.createSpyObj("adhHttpMock", ["put", "get", "post"]);
                adhHttpMock.put.and.returnValue(Util.mkPromise(q, {}));
                adhHttpMock.post.and.returnValue(Util.mkPromise(q, {}));
                adhHttpMock.get.and.returnValue(Util.mkPromise(q, {
                    data: {
                        "adhocracy.resources.principal.IUsersPool": {}
                    }
                }));

                httpMock = {
                    defaults: {
                        headers: {
                            common: {}
                        }
                    }
                };

                windowMock = {
                    localStorage: <any>jasmine.createSpyObj("localStorage", ["getItem", "setItem", "removeItem"])
                };
                windowMock.localStorage.getItem.and.returnValue(null);

                modernizrMock = {
                    localstorage: true
                };

                adhUser = new AdhUser.User(adhHttpMock, q, httpMock, windowMock, modernizrMock);
            });

            describe("login", () => {
                beforeEach(() => {
                    adhUser.adhHttp.put.and.returnValue(Util.mkPromise(q, {
                        status: "success",
                        user_path: "user1_path",
                        user_token: "user1_tok"
                    }));

                    expect(adhUser.loggedIn).toBe(false);
                    expect(adhUser.data).not.toBeDefined();
                });

                var testLogin = () => {
                    it("sets loggedIn to true", () => {
                        expect(adhUser.loggedIn).toBe(true);
                    });
                    it("sets data to the user resource", () => {
                        // FIXME: Use actual user schema
                        expect(adhUser.data).toBeDefined();
                    });
                    it("sets token to the session token", () => {
                        expect(adhUser.token).toBe("user1_tok");
                    });
                    it("sets default http headers for the http service", () => {
                        expect(httpMock.defaults.headers.common["X-User-Token"]).toBe("user1_tok");
                        expect(httpMock.defaults.headers.common["X-User-Path"]).toBe("user1_path");
                    });
                };

                describe("happy login flow with username and password", () => {
                    beforeEach((done) => {
                        adhUser.logIn("user1", "user1_pass").then(done);
                    });

                    testLogin();

                    it("requests the API endpoint /login_username", () => {
                        expect(adhHttpMock.put).toHaveBeenCalledWith("/login_username", {
                            name: "user1",
                            password: "user1_pass"
                        });
                    });

                    it("stores user token and user path in localstorage", () => {
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-token", "user1_tok");
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-path", "user1_path");
                    });
                });

                describe("happy login flow with email and password", () => {
                    beforeEach((done) => {
                        adhUser.logIn("user1@somedomain", "user1_pass").then(done);
                    });

                    testLogin();

                    it("requests the API endpoint /login_email", () => {
                        expect(adhHttpMock.put).toHaveBeenCalledWith("/login_email", {
                            email: "user1@somedomain",
                            password: "user1_pass"
                        });
                    });

                    it("stores user token and user path in localstorage", () => {
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-token", "user1_tok");
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-path", "user1_path");
                    });
                });

                describe("localstorage unavailable", () => {
                    beforeEach((done) => {
                        modernizrMock.localstorage = false;
                        adhUser.logIn("user1", "user1_pass").then(done);
                    });

                    testLogin();
                });

                describe("request fails", () => {
                    var _reason;

                    beforeEach((done) => {
                        adhUser.adhHttp.put.and.returnValue(q.reject());
                        adhUser.logIn("user1", "user1_wrong_pass").then(
                            done,
                            (reason) => {
                                _reason = reason;
                                done();
                            }
                        );
                    });

                    it("rejects the login attempt", () => {
                        expect(_reason).toBe("invalid credentials");
                        expect(adhUser.loggedIn).toBe(false);
                        expect(adhUser.data).not.toBeDefined();
                        expect(adhUser.token).not.toBeDefined();
                        expect(httpMock.defaults.headers.common["X-User-Token"]).not.toBeDefined();
                        expect(httpMock.defaults.headers.common["X-User-Path"]).not.toBeDefined();
                    });
                });
            });

            describe("register", () => {
                beforeEach((done) => {
                    adhUser.register("username", "email", "password", "passwordRepeat").then(done);
                });

                it("posts to '/principals/users/'", () => {
                    var args = adhHttpMock.post.calls.mostRecent().args;
                    expect(args[0]).toBe("/principals/users/");
                });
                it("posts a valid user resource", () => {
                    var data = adhHttpMock.post.calls.mostRecent().args[1].data;
                    expect(data["adhocracy.sheets.user.UserBasicSchema"].name).toBe("username");
                    expect(data["adhocracy.sheets.user.UserBasicSchema"].email).toBe("email");
                    expect(data["adhocracy.sheets.user.IPasswordAuthentication"].password).toBe("password");
                });
            });
        });
    });
};
