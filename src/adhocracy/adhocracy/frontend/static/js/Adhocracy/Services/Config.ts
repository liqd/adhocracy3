/**
 * simple config mechanism.  exported as a service to allow for
 * injecting an alternative config object in tests.  (there are many
 * obvious design changes, but that is future work: without more
 * sophisticated requirements, not much can be gained from
 * implementing them.)
 */

export interface Type {
    root_path: string;
    template_path: string;
    ws_url: string;
}

var config : Type = {
    rootPath: "/adhocracy",
    templatePath: "/frontend_static/templates",
    wsUrl: "ws://localhost:8080/"
};


export var register = (app, serviceName) => {
    app.factory(serviceName, () => config);
};

