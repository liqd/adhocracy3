export class User {
    loggedIn : boolean = false;
    name : string;
    token : string;

    constructor(public $http : ng.IHttpService, public $window : Window, public Modernizr) {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            if (_self.$window.localStorage.getItem("user-token") !== null) {
                // FIXME: check if user-token is still valid and get user data from server
                _self.setToken(this.$window.localStorage.getItem("user-token"));
                _self.loggedIn = true;
            }
        }
    }

    private setToken(token : string) {
        var _self : User = this;

        _self.token = token;
        _self.$http.defaults.headers.common["X-User-Token"] = token;
        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.setItem("user-token", token);
        } else {
            console.log("session could not be persisted");
        }
    }

    private deleteToken() {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.removeItem("user-token");
        }
        delete _self.$http.defaults.headers.common["X-User-Token"];
        _self.token = undefined;
    }

    logIn(nameOrEmail : string, password : string) {
        var _self : User = this;

        // FIXME this is only a dummy implementation
        _self.name = nameOrEmail;
        _self.setToken(nameOrEmail);
        _self.loggedIn = true;
    }

    logOut() {
        var _self : User = this;

        // FIXME this is only a dummy implementation
        _self.loggedIn = false;
        _self.deleteToken();
        _self.name = undefined;
    }

    can(permission : string) {
        var _self : User = this;

        // FIXME this is only a dummy implementation
        return _self.loggedIn;
    }
}

export var loginDirective = ($$user : User) => {
    return {
        restrict: "E",
        templateUrl: "/frontend_static/templates" + "/Login.html",
        scope: {},
        controller: ["$scope", function($scope) : void {
            $scope.user = $$user;
            $scope.credentials = {
                nameOrEmail: "",
                password: ""
            };

            $scope.resetCredentials = function() {
                $scope.credentials.nameOrEmail = "";
                $scope.credentials.password = "";
            };
            $scope.logIn = function() {
                $scope.user.logIn($scope.credentials.nameOrEmail, $scope.credentials.password);
                $scope.resetCredentials();
            };
            $scope.logOut = function() {
                $scope.user.logOut();
            };
        }]
    };
};

export var registerDirective = (adhConfig) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Register.html",
        scope: { },
        controller: ["$scope", "adhHttp", ($scope, adhHttp) => {
            $scope.postRegistration = (): void => {

                // FIXME: sanity check input some more
                // (password_repeat, do not post if email smells
                // funny, ...)

                adhHttp.post("/principals/users/", {
                    "content_type": "adhocracy.resources.principal.IUser",
                    "data": {
                        "adhocracy.sheets.user.UserBasicSchema": {
                            "name": $scope.username,
                            "email": $scope.email
                        },
                        "adhocracy.sheets.user.IPasswordAuthentication": {
                            "password": $scope.password
                        }
                    }
                }).then(() => {
                    throw "handler for registration response not implemented.";
                });
            };
        }]
    };
};
