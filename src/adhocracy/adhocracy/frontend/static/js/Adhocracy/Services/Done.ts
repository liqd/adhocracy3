/**
 * This service is just a dummy callback.  You can use it wherever
 * dependency injection is used and where you want to be able to inject
 * a real callback in your tests.
 */
var done = () => {
    return;
};

export var register = (app, serviceName : string) => {
    app.factory(serviceName, () => done);
};
