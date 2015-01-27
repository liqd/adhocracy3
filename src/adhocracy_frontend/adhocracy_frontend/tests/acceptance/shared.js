var annotatorLogin = "annotator";
var annotatorPassword = "password";

var restUrl = "http://localhost:6542/";


var LoginPage = function() {
    this.loginInput = element(by.name("nameOrEmail"));
    this.passwordInput = element(by.name("password"));
    this.submitButton = element(by.css(".login [type=\"submit\"]"));

    this.get = function() {
        browser.get("/login");
    };

    this.login = function(username, password) {
        this.loginInput.sendKeys(username);
        this.passwordInput.sendKeys(password);
        this.submitButton.click();
        browser.waitForAngular();
    };
};



var login = function(username, password) {
    var loginPage = new LoginPage();
    loginPage.get();
    loginPage.login(username, password);
};


var loginAnnotator = function() {
    login(annotatorLogin, annotatorPassword);
};


module.exports = {
    restUrl: restUrl,
    login: login,
    loginAnnotator: loginAnnotator
}
