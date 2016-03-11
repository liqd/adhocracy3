/// <reference path="../../../lib2/types/angular.d.ts"/>

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

var extractErrorItems = (code : number, error : IBackendError) : IBackendErrorItem[] => {
    if (code === 410) {
        return [{
            location: "url",
            name: "GET",
            description: (<any>error).reason
        }];
    } else {
        return error.errors;
    }
};

export var logBackendError = (response : angular.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    console.log(response);

    throw extractErrorItems(response.status, response.data);
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
export var logBackendBatchError = (
    response : angular.IHttpPromiseCallbackArg<{
        responses : {
            code : number;
            body? : IBackendError;
        }[];
    }>
) : void => {
    "use strict";

    console.log(response);

    var lastResponse = response.data.responses[response.data.responses.length - 1];
    throw extractErrorItems(lastResponse.code, lastResponse.body);
};


export var formatError = (error : IBackendErrorItem) : string => {
    if (error.location === "internal") {
        return "Internal Error";
    } else {
        return error.description;
    }
};
