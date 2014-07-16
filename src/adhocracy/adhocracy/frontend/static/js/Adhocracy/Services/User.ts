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
            if (_self.$window.localStorage.getItem("user-token") !== null) {
                // FIXME: check if user-token is still valid and get user data from server
                _self.enableToken(
                    this.$window.localStorage.getItem("user-token"),
                    this.$window.localStorage.getItem("user-path")
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
                _self.$q.reject("failed to fetch user resource");
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
            promise = _self.adhHttp.put("/login_username", {
                name: nameOrEmail,
                password: password
            });
        } else {
            promise = _self.adhHttp.put("/login_email", {
                email: nameOrEmail,
                password: password
            });
        }

        return promise
            .then((response) => {
                // FIXME use websockets for updates
                return _self.storeAndEnableToken(response.user_token, response.user_path);
            }, (reason) => {
                // FIXME server does not send details on what went wrong.
                // This may also be an internal server error or similar.
                return _self.$q.reject("invalid credentials");
            });
    }

    logOut() {
        var _self : User = this;

        // The server does not have a logout yet.
        _self.deleteToken();
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
