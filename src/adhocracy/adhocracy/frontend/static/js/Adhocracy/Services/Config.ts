// simple config mechanism.  exported as a service to allow for
// injecting an alternative config object in tests.  (there are many
// obvious design changes, but that is future work: without more
// sophisticated requirements, not much can be gained from
// implementing them.)

export interface Type {
    templatePath: string;
    jsonPrefix: string;
    wsuri: string;
}

var config : Type = {
    templatePath: "/frontend_static/templates",
    jsonPrefix: "/adhocracy",
    wsuri:  "ws://" + window.location.host + "/adhocracy?ws=all"
};


export var register = function(app, serviceName) {
    app.factory(serviceName, () => config);
};
