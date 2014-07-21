export interface IUserBasic {
    name? : string;
    email? : string;
    tzname? : string;
}


export class User {
    loggedIn : boolean = false;
    token : string;
    data : IUserBasic;

    constructor(
        public adhHttp,
        public $q,
        public $http : ng.IHttpService,
        public $window : Window,
        public Modernizr
    ) {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            if (_self.$window.localStorage.getItem("user-token") !== null &&
                    _self.$window.localStorage.getItem("user-path") !== null) {
                _self.enableToken(
                    _self.$window.localStorage.getItem("user-token"),
                    _self.$window.localStorage.getItem("user-path")
                );
            }
        }
    }

    private enableToken(token : string, userPath : string) : void {
        var _self : User = this;

        _self.token = token;
        _self.$http.defaults.headers.common["X-User-Token"] = token;
        _self.$http.defaults.headers.common["X-User-Path"] = userPath;
        _self.loggedIn = true;

        return _self.adhHttp.get(userPath)
            .then((resource) => {
                _self.data = resource.data["adhocracy.resources.principal.IUsersPool"];
            }, (reason) => {
                // The user resource that was returned by the server could not be accessed.
                // This may happen e.g. with a network disconnect
                _self.deleteToken();
                return _self.$q.reject("failed to fetch user resource");
            });
    }

    private storeAndEnableToken(token : string, userPath : string) : void {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.setItem("user-token", token);
            _self.$window.localStorage.setItem("user-path", userPath);
        } else {
            console.log("session could not be persisted");
        }

        return _self.enableToken(token, userPath);
    }

    private deleteToken() {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.removeItem("user-token");
            _self.$window.localStorage.removeItem("user-path");
        }
        delete _self.$http.defaults.headers.common["X-User-Token"];
        delete _self.$http.defaults.headers.common["X-User-Path"];
        _self.token = undefined;
        _self.data = undefined;
        _self.loggedIn = false;
    }

    logIn(nameOrEmail : string, password : string) {
        var _self : User = this;
        var promise;

        if (nameOrEmail.indexOf("@") === -1) {
            promise = _self.adhHttp.post("/login_username", {
                name: nameOrEmail,
                password: password
            });
        } else {
            promise = _self.adhHttp.post("/login_email", {
                email: nameOrEmail,
                password: password
            });
        }

        return promise
            .then((response) => {
                // FIXME use websockets for updates
                return _self.storeAndEnableToken(response.user_token, response.user_path);
            });
    }

    logOut() {
        var _self : User = this;

        // The server does not have a logout yet.
        _self.deleteToken();
    }

    register(username : string, email : string, password : string, passwordRepeat : string) {
        var _self : User = this;

        return _self.adhHttp.post("/principals/users/", {
            "content_type": "adhocracy.resources.principal.IUser",
            "data": {
                "adhocracy.sheets.user.UserBasicSchema": {
                    "name": username,
                    "email": email
                },
                "adhocracy.sheets.user.IPasswordAuthentication": {
                    "password": password
                }
            }
        });
    }

    can(permission : string) {
        var _self : User = this;

        // FIXME this is only a dummy implementation
        return _self.loggedIn;
    }
}

export var loginDirective = (adhConfig) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Login.html",
        scope: {},
        controller: ["adhUser", "$scope", (adhUser : User, $scope) : void => {
            $scope.credentials = {
                nameOrEmail: "",
                password: ""
            };

            $scope.resetCredentials = () => {
                $scope.credentials.nameOrEmail = "";
                $scope.credentials.password = "";
            };
            $scope.logIn = () => {
                var promise = adhUser.logIn($scope.credentials.nameOrEmail, $scope.credentials.password).then(() => {
                    $scope.error = undefined;
                }, (errors) => {
                    $scope.error = errors.length ? errors[0].description : "Internal Error";
                });
                $scope.resetCredentials();
                return promise;
            };
            $scope.logOut = () => {
                adhUser.logOut();
            };
        }]
    };
};

export var registerDirective = (adhConfig, $location) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Register.html",
        scope: {},
        controller: ["adhUser", "$scope", (adhUser, $scope) => {
            $scope.input = {
                username: "",
                email: "",
                password: "",
                passwordRepeat: ""
            };

            $scope.register = () : void => {
                return adhUser.register($scope.input.username, $scope.input.email, $scope.input.password, $scope.input.passwordRepeat)
                    .then(() => {
                        $scope.error = undefined;
                        $location.path("/frontend_static/root.html");
                    }, (errors) => {
                        $scope.error = errors.length ? errors[0].description : "Internal Error";
                    });
            };
        }]
    };
};
