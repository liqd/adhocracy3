/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

// Error responses in the Adhocracy REST API contain json objects in
// the body that have the following form:
export interface IBackendError {
    status: string;
    errors: IBackendErrorItem[];
}

export interface IBackendErrorItem {
    name : string;
    location : string;
    description : string;
}

export var logBackendError = (response : ng.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    console.log("http response with error status: " + response.status);

    for (var e in response.data.errors) {
        if (response.data.errors.hasOwnProperty(e)) {
            console.log("error #" + e);
            console.log("where: " + response.data.errors[e].name + ", " + response.data.errors[e].location);
            console.log("what:  " + response.data.errors[e].description);
        }
    }

    console.log(response.config);
    console.log(response.data);

    throw response.data.errors;
};
