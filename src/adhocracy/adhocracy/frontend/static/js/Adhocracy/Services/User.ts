export class User {
    loggedIn : boolean = false;
    name : string;
    token : string;

    constructor(
        public adhHttp,
        public $q,
        public $http : ng.IHttpService,
        public $window : Window,
        public Modernizr
    ) {
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
                _self.loggedIn = true;
                _self.setToken(response.user_token);

                return _self.adhHttp.get(response.user_path)
                    .then((data) => {
                        _self.data = data;
                    }, (reason) => {
                        // The user resource that was returned by the server could not be accessed.
                        // This is an internal error.
                        _self.deleteToken();
                        _self.loggedIn = false;
                        _self.$q.reject("internal error");
                    });
            }, (reason) => {
                // FIXME server does not send details on what went wrong.
                // This may also be an internal server error or similar.
                _self.$q.reject("invalid credentials");
            });
    }

    logOut() {
        var _self : User = this;

        // The server does not have a logout yet.
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
