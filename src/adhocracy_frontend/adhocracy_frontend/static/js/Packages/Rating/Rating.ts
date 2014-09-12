import AdhResource = require("../../Resources");
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
    cast(RatingValue) : void;
    update() : void;
}


export interface IRatingAdapter<T extends AdhResource.Content<any>> {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
    content(resource : T) : string;
    content(resource : T, value : string) : T;
    refersTo(resource : T) : string;
    refersTo(resource : T, value : string) : T;
    creator(resource : T) : string;
    creationDate(resource : T) : string;
    modificationDate(resource : T) : string;
}


export var createDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Rating.html",
        scope: {
            refersTo: "@"
        },
        link: (scope : IRatingScope) => {
            scope.cast = (rating : RatingValue) : void => {
                if (scope.isActive(rating)) {
                    scope.ratings[RatingValue[rating]] -= 1;
                    delete scope.active;
                } else {
                    // decrease old value
                    if (scope.hasOwnProperty("active")) {
                        scope.ratings[RatingValue[scope.active]] -= 1;
                    }
                    // increase new value
                    scope.ratings[RatingValue[rating]] += 1;
                    scope.active = rating;
                }
            };

            delete scope.active;
            scope.isActive = (rating : RatingValue) => (rating === scope.active) ? "rating-button-active" : "";

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
