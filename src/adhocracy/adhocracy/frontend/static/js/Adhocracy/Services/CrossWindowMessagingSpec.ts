/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import CrossWindowMessaging = require("./CrossWindowMessaging");

export var register = () => {

    describe("Services/CrossWindowMessaging", () => {

        var postMessageMock = <any>jasmine.createSpy("postMessageMock");
        var service = new CrossWindowMessaging.Service(postMessageMock);

        it("calls window.postMessage with given resize parameters", () => {

            service.postResize(280);
            var args = postMessageMock.calls.mostRecent().args;
            expect(JSON.parse(args)).toEqual({
                name: "resize",
                data: {height: 280},
                sender: 0
            });
        });
    });
};
