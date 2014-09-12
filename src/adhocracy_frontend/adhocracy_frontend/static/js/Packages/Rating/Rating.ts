import AdhConfig = require("../Config/Config");

var pkgLocation = "/Rating";


export enum RatingValue {
    pro,
    contra,
    neutral
};


export interface IRatingScope extends ng.IScope {
    refersTo : string;
    ratings : {
        pro : number;
        contra : number;
        neutral : number;
    };
    active : RatingValue;
    isActive : (RatingValue) => string;  // css class name if RatingValue is active, or "" otherwise.
    cast(value : RatingValue) : void;
    update() : void;
}


export var createDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Rating.html",
        scope: {
            refersTo: "@"
        },
        link: (scope : IRatingScope) => {
            scope.cast = (value : RatingValue) : void => {
                if (scope.isActive(value)) {
                    scope.ratings[RatingValue[value]] -= 1;
                    delete scope.active;
                } else {
                    // decrease old value
                    if (scope.hasOwnProperty("active")) {
                        scope.ratings[RatingValue[scope.active]] -= 1;
                    }
                    // increase new value
                    scope.ratings[RatingValue[value]] += 1;
                    scope.active = value;
                }
            };

            delete scope.active;
            scope.isActive = (value : RatingValue) => (value === scope.active) ? "rating-button-active" : "";

            scope.update = () : void => {
                // FIXME: This sets some arbitrary data for now.
                // Instead, this should get the data from the server.
                scope.ratings = {
                    pro: 10,
                    contra: 5,
                    neutral: 3
                };
            };

            scope.update();
        }
    };
};
