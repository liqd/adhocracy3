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

var renderBackendError = (errors : IBackendErrorItem[]) : void => {
    for (var e in errors) {
        if (errors.hasOwnProperty(e)) {
            console.log("error #" + e);
            console.log("where: " + errors[e].name + ", " + errors[e].location);
            console.log("what:  " + errors[e].description);
        }
    }
};

export var logBackendError = (response : ng.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    var errors = response.data.errors;

    console.log("http response with error status: " + response.status);
    console.log(response.config);
    console.log(response.data);

    renderBackendError(errors);
    throw errors;
};

/**
 * batch requests recive an array of responses.  each response matches
 * one request that was actually processed in the backend.  Since the
 * first error makes batch processing stop, all responses up to the
 * last one are successes.  If this function is called, the error is
 * contained in the last element of the array.  All other elements are
 * ignored by this function.
 */
export var logBackendBatchError = (response : ng.IHttpPromiseCallbackArg<IBackendError[]>) : void => {
    "use strict";

    console.log("http batch response with error status: " + response.status);
    console.log(response.config);

    if (response.data.length < 1) {
        throw "no batch item responses!";
    }

    var lastBatchItemResponse : IBackendError = (<any>(response.data[response.data.length - 1])).body;
    console.log(lastBatchItemResponse);

    var errors : IBackendErrorItem[] = lastBatchItemResponse.errors;
    // In rest_api.rst, we call the response body field 'body', but
    // $http calls it 'data'.  `logBackendBatchError` and
    // `importBatchContent` are the only two places where this gets a
    // little confusing.  It could be fixed in rest_api.rst, the
    // backend, and then in these two functions.

    // Workaround for backend bug.  See redmine ticket #1466.
    if (errors.length > 0 && !errors[0].hasOwnProperty("name")) {
        var es = errors.map((a) => { return { name: a[0], location: a[1], description: a[2] }; });
        errors = es;
    }

    renderBackendError(errors);
    throw errors;
};