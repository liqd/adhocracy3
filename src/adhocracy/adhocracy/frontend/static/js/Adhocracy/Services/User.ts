export class User {
    loggedIn : boolean = false;
    name : string;
    token : string;

    constructor(public $http : ng.IHttpService) {}

    private setToken(token : string) {
        this.token = token;
        this.$http.defaults.headers.common["X-User-Token"] = token;
        // FIXME set cookie for persistance
    }

    private deleteToken() {
        // FIXME delete cookie
        delete this.$http.defaults.headers.common["X-User-Token"];
        this.token = undefined;
    }

    logIn(nameOrEmail : string, password : string) {
        // FIXME this is only a dummy implementation
        this.name = nameOrEmail;
        this.setToken(nameOrEmail);
        this.loggedIn = true;
    }

    logOut() {
        // FIXME this is only a dummy implementation
        this.loggedIn = false;
        this.deleteToken();
        this.name = undefined;
    }

    can(permission : string) {
        // FIXME this is only a dummy implementation
        return this.loggedIn;
    }
}

export var loginDirective = ($$user : User) => {
    return {
        restrict: "E",
        templateUrl: "/frontend_static/templates" + "/Util/login.html",
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
