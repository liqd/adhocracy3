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
 *
 * NOTE: See documentation of `importBatchContent`.
 */
export var logBackendBatchError = (response : ng.IHttpPromiseCallbackArg<IBackendError[]>) : void => {
    "use strict";

    // if the response list has length 1, the backend does not bother
    // with the brackets, and just sends the single list item without
    // the list.  FIXME: the only reasonable thing is for the backend
    // to always send a list, even if it only contains one element!
    if (!response.data.hasOwnProperty("length")) {
        response.data = [<any>response.data];
    }

    console.log("http batch response with error status: " + response.status);
    console.log(response.config);

    if (response.data.length < 1) {
        throw "no batch item responses!";
    }

    var lastBatchItemResponse : IBackendError = response.data[response.data.length - 1];
    console.log(lastBatchItemResponse);

    var errors : IBackendErrorItem[] = lastBatchItemResponse.errors;

    renderBackendError(errors);
    throw errors;
};
