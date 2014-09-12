import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhResource = require("../../Resources");
import AdhUser = require("../User/User");
import ResourcesBase = require("../../ResourcesBase");

var pkgLocation = "/Rating";


export enum RatingValue {
    pro,
    contra,
    neutral
};


export interface IRatingScope extends ng.IScope {
    refersTo : string;
    postPoolSheet : string;
    postPoolField : string;
    ratings : {
        pro : number;
        contra : number;
        neutral : number;
    };
    thisUsersRating : ResourcesBase.Resource;
    active : RatingValue;
    isActive : (RatingValue) => string;  // css class name if RatingValue is active, or "" otherwise.
    cast(RatingValue) : void;

    // these functions should be private to the controller, but we
    // need to export them somehow for jasmine, and we want to
    // implement them inside the controller because we need its local
    // variables.
    postPoolPathPromise : ng.IPromise<string>;
    resetRatings() : void;
    updateRatings() : ng.IPromise<void>;
}


// (this type is over-restrictive in that T is used for both the
// rating, the subject, and the target.  luckily, subtype-polymorphism
// is too cool to complain about it here.  :-)
export interface IRatingAdapter<T extends AdhResource.Content<any>> {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
    content(resource : T) : string;
    content(resource : T, value : string) : T;
    subject(resource : T) : string;
    subject(resource : T, value : string) : T;
    target(resource : T) : string;
    target(resource : T, value : string) : T;
    creator(resource : T) : string;
    creationDate(resource : T) : string;
    modificationDate(resource : T) : string;
}


export var ratingController = (
    adapter : IRatingAdapter<any>,
    $scope : IRatingScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User
) => {

    // fetch post pool path with coordinates given in scope
    $scope.postPoolPathPromise =
        adhHttp.get($scope.refersTo).then((rateable : ResourcesBase.Resource) => {
            if (rateable.hasOwnProperty("data")) {
                if (rateable.data.hasOwnProperty($scope.postPoolSheet)) {
                    if (rateable.data[$scope.postPoolSheet].hasOwnProperty($scope.postPoolField)) {
                        return rateable.data[$scope.postPoolSheet][$scope.postPoolField];
                    }
                }
            }

            throw "post pool field in " + $scope.postPoolSheet + "/" + $scope.postPoolField +
                " not found in content type " + rateable.content_type;
        });

    // initialise ratings
    $scope.resetRatings = () => {
        $scope.ratings = {
            pro: 0,
            contra: 0,
            neutral: 0
        };

        delete $scope.thisUsersRating;
    };

    // Update state from server: Fetch post pool, query it for all
    // ratings, and store and render them.  If a rating of the current
    // user exists, store and render that separately.
    $scope.updateRatings = () : ng.IPromise<void> =>
        $scope.postPoolPathPromise.then((postPoolPath) =>
            adhHttp.get(postPoolPath).then((pool) => {
                var ratingPromises : ng.IPromise<ResourcesBase.Resource>[] =
                    pool.data["adhocracy.sheets.pool.IPool"].elements
                        .map((index : number, path : string) => adhHttp.get(path));

                $q.all(ratingPromises).then((ratings) => {
                    $scope.resetRatings();
                    _.forOwn(ratings, (rating) => {

                        // FIXME: these need to be calculated properly, not just declared!
                        var __ispro;
                        var __iscontra;
                        var __isneutral;
                        var __iscurrentuser;

                        if (__ispro) {
                            $scope.ratings.pro += 1;
                        }

                        if (__iscontra) {
                            $scope.ratings.contra += 1;
                        }

                        if (__isneutral) {
                            $scope.ratings.neutral += 1;
                        }

                        if (__iscurrentuser) {
                            $scope.thisUsersRating = rating;
                        }
                    });
                });
            }));

    $scope.resetRatings();
    $scope.updateRatings();
};


export var createDirective = (adapter : IRatingAdapter<any>, adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Rating.html",
        scope: {
            refersTo: "@",
            postPoolSheet : "@",
            postPoolField : "@"
        },
        link: (scope : IRatingScope) => {
            scope.cast = (rating : RatingValue) : void => {
                if (scope.isActive(rating)) {
                    // click on active button to un-rate

                    scope.ratings[RatingValue[rating]] -= 1;
                    delete scope.active;
                } else {
                    // click on inactive button to (re-)rate

                    // decrease old value
                    if (scope.hasOwnProperty("active")) {
                        scope.ratings[RatingValue[scope.active]] -= 1;
                    }
                    // increase new value
                    scope.ratings[RatingValue[rating]] += 1;
                    scope.active = rating;
                }
            };

            scope.isActive = (rating : RatingValue) =>
                (rating === scope.active) ? "rating-button-active" : "";
        },
        controller: ["$scope", "$q", "adhHttp", "adhUser", ($scope, $q, adhHttp, adhUser) =>
            ratingController(adapter, $scope, $q, adhHttp, adhUser)]
    };
};
