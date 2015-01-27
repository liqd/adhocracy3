// conf.js
exports.config = {
    specs: ["../src/adhocracy_frontend/adhocracy_frontend/tests/acceptance/*Spec.js"],
    baseUrl: "http://localhost:6552",
    directConnect: true,
    capabilities: {
        "browserName": "chrome"
    }
}
