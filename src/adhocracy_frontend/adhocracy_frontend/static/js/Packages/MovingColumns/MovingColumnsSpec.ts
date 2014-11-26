/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import AdhMovingColumns = require("./MovingColumns");

export var register = () => {
    describe("MovingColumns", () => {
        describe("MovingColumns", () => {
            var directive;
            var topLevelStateMock;

            beforeEach(() => {
                topLevelStateMock = <any>jasmine.createSpyObj("topLevelStateMock", ["on", "get"]);
                directive = AdhMovingColumns.movingColumns(topLevelStateMock);
                topLevelStateMock.get.and.callFake((key) => {
                    return {
                        something: "something",
                        movingColumns: "initial"
                    }[key];
                });
            });

            describe("link", () => {
                var scopeMock;
                var elementMock;
                var attrsMock;

                beforeEach(() => {
                    scopeMock = {};
                    attrsMock = {
                        something: "something"
                    };
                    elementMock = <any>jasmine.createSpyObj("elementMock", ["addClass", "removeClass"]);

                    var link = directive.link;
                    link(scopeMock, elementMock, attrsMock);
                });

                describe("on MovingColumns", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.on.calls.argsFor(3)[1];
                    });

                    it("adds class 'is-collapse-show-show' if state is collapse-show-show", () => {
                        callback("is-collapse-show-show");
                        expect(elementMock.addClass).toHaveBeenCalledWith("is-collapse-show-show");
                    });

                    it("removes class 'is-collapse-show-show' if columns is show-show-hide", () => {
                        callback("is-collapse-show-show");
                        callback("is-show-show-hide");
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-collapse-show-show");
                    });

                    it("adds class 'is-show-show-hide' if state is show-show-hide", () => {
                        callback("is-show-show-hide");
                        expect(elementMock.addClass).toHaveBeenCalledWith("is-show-show-hide");
                    });

                    it("removes class 'is-show-show-hide' if columns is show-show-hide", () => {
                        callback("is-show-show-hide");
                        callback("is-collapse-show-show");
                        expect(elementMock.removeClass).toHaveBeenCalledWith("is-show-show-hide");
                    });
                });

                describe("on Content2Url", () => {
                    var callback;

                    beforeEach(() => {
                        callback = topLevelStateMock.on.calls.argsFor(0)[1];
                    });

                    it("sets content2Url in scope", () => {
                        callback("some/path");
                        expect(scopeMock.content2Url).toBe("some/path");
                    });
                });
            });
        });
    });
};
