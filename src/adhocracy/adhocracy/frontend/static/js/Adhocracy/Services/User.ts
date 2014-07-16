export interface IUserResource {

}


export class User {
    loggedIn : boolean = false;
    name : string;
    token : string;
    data : IUserResource;

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

    private enableToken(token : string, user_path : string) : void {
        var _self : User = this;

        _self.token = token;
        _self.$http.defaults.headers.common["X-User-Token"] = token;
        _self.loggedIn = true;

        return _self.adhHttp.get(user_path)
            .then((data) => {
                _self.data = data;
            }, (reason) => {
                // The user resource that was returned by the server could not be accessed.
                // This may happen e.g. with a network disconnect
                _self.deleteToken();
                _self.loggedIn = false;
                _self.$q.reject("failed to fetch user resource");
            });
    }

    private storeAndEnableToken(token : string, user_path : string) : void {
        var _self : User = this;

        if (_self.Modernizr.localstorage) {
            _self.$window.localStorage.setItem("user-token", token);
            _self.$window.localStorage.setItem("user-path", user_path);
        } else {
            console.log("session could not be persisted");
        }

        return _self.enableToken(token, user_path);
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
