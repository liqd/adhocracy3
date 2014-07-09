/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>

import CrossWindowMessaging = require("./CrossWindowMessaging");

export var register = () => {

    xdescribe("Services/CrossWindowMessaging", () => {

        var postMessageMock = <any>jasmine.createSpy("postMessageMock");
        var windowMock = <any>jasmine.createSpyObj("windowMock", ["addEventListener"]);
        // var service = new CrossWindowMessaging.Service(postMessageMock, windowMock);  // REVIEW: type error!
        var service: any;

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
