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
