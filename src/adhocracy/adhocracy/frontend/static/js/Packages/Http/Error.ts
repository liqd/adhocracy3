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

export var logBackendBatchError = (response : ng.IHttpPromiseCallbackArg<IBackendError[]>) : void => {
    "use strict";

    console.log("http batch response with error status: " + response.status);
    console.log(response.config);
    console.log(response.data);

    if (response.data.length < 1) {
        throw "no batch item responses!";
    }

    var lastBatchItemResponse = response.data[response.data.length - 1];
    var errors = (<any>lastBatchItemResponse).body.errors;
    // In rest_api.rst, we call the response body field 'body', but
    // $http calls it 'data'.  `logBackendBatchError` and
    // `importBatchContent` are the only two places where this gets a
    // little confusing.  It could be fixed in rest_api.rst, the
    // backend, and then in these two functions.

    // Workaround for backend bug.  See redmine ticket #1466.
    errors = errors.map((a) => { return { name: a[0], location: a[1], description: a[2] }; });

    renderBackendError(errors);
    throw errors;
};
