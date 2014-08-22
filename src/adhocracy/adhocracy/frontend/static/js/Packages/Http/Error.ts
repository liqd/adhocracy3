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

var renderBackendError = (es : IBackendErrorItem[]) : string => {
    var v = "";

    for (var e in es) {
        if (es.hasOwnProperty(e)) {
            v += "error #" + e + "\n";
            v += "where: " + es[e].name + ", " + es[e].location + "\n";
            v += "what:  " + es[e].description;
        }
    }

    return v;
};

export var logBackendError = (response : ng.IHttpPromiseCallbackArg<IBackendError>) : void => {
    "use strict";

    var es = response.data.errors;

    console.log("http response with error status: " + response.status);
    console.log(response.config);
    console.log(response.data);

    console.log(renderBackendError(es));
    throw es;
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
    var es = (<any>lastBatchItemResponse).body.errors;
    // In rest_api.rst, we call the response body field 'body', but
    // $http calls it 'data'.  `logBackendBatchError` and
    // `importBatchContent` are the only two places where this gets a
    // little confusing.  It could be fixed in rest_api.rst, the
    // backend, and then in these two functions.

    // Workaround for backend bug.  See redmine ticket #1466.
    var es = es.map((a) => { return { name: a[0], location: a[1], description: a[2] }});

    console.log(renderBackendError(es));
    throw es;
};
