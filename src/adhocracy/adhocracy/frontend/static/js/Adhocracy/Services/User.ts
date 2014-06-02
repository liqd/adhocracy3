export class User {
    loggedIn : boolean = false;
    name : string;
    displayName : string;

    logIn(name : string, password : string) {
        // FIXME this is only a dummy implementation
        this.name = name;
        this.displayName = name;
        this.loggedIn = true;
    }

    logOut() {
        // FIXME this is only a dummy implementation
        this.loggedIn = false;
        this.name = undefined;
        this.displayName = undefined;
    }

    can(permission : string) {
        // FIXME this is only a dummy implementation
        return this.loggedIn;
    }
}

var loginDirective = function($$user : User) {
    return {
        restrict: "E",
        templateUrl: "/frontend_static/templates" + "/Util/login.html",
        scope: {},
        controller: ["$scope", function($scope) : void {
            $scope.user = $$user;
            $scope.credentials = {
                name: "",
                password: ""
            };

            $scope.resetCredentials = function() {
                $scope.credentials.name = "";
                $scope.credentials.password = "";
            };
            $scope.logIn = function() {
                $scope.user.logIn($scope.credentials.name, $scope.credentials.password);
                $scope.resetCredentials();
            };
            $scope.logOut = function() {
                $scope.user.logOut();
            };
        }]
    };
};

export var register = function(app, serviceName : string, loginDirectiveName : string) {
    app.factory(serviceName, function() : User {
        return new User();
    });
    app.directive(loginDirectiveName, [serviceName, loginDirective]);
};
