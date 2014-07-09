/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import CrossWindowMessaging = require("./CrossWindowMessaging");

export var register = () => {

    describe("Services/CrossWindowMessaging", () => {

        var postMessageMock = <any>jasmine.createSpy("postMessageMock");
        var windowMock = <any>jasmine.createSpyObj("windowMock", ["addEventListener"]);
        var intervalMock = jasmine.createSpy("intervalMock");
        var service = new CrossWindowMessaging.Service(postMessageMock, windowMock, intervalMock);

        it("calls window.postMessage with given resize parameters", () => {

            service.postResize(280);
            var args = postMessageMock.calls.mostRecent().args;
            expect(JSON.parse(args[0])).toEqual({
                name: "resize",
                data: {height: 280}
            });
        });
    });
};
