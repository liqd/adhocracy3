import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
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
    thisUsersRating : any;  // resource matching IRatingAdapter (this is tricky to type, so we leave it blank for now.)
    isActive : (RatingValue) => string;  // css class name if RatingValue is active, or "" otherwise.
    cast(RatingValue) : void;
    assureUserRatingExists() : ng.IPromise<void>;
    postUpdate() : ng.IPromise<void>;
}


// (this type is over-restrictive in that T is used for both the
// rating, the subject, and the target.  luckily, subtype-polymorphism
// is too cool to complain about it here.  :-)
export interface IRatingAdapter<T extends AdhResource.Content<any>> {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
    subject(resource : T) : string;
    subject(resource : T, value : string) : T;
    target(resource : T) : string;
    target(resource : T, value : string) : T;
    value(resource : T) : RatingValue;
    value(resource : T, value : RatingValue) : T;
    creator(resource : T) : string;
    creationDate(resource : T) : string;
    modificationDate(resource : T) : string;
}


/**
 * initialise ratings
 */
export var resetRatings = ($scope : IRatingScope) : void => {
    $scope.ratings = {
        pro: 0,
        contra: 0,
        neutral: 0
    };

    delete $scope.thisUsersRating;
};


/**
 * fetch post pool path with coordinates given in scope
 */
export var postPoolPathPromise = (
    $scope : IRatingScope,
    adhHttp : AdhHttp.Service<any>
) : ng.IPromise<string> => {
    return adhHttp.get($scope.refersTo).then((rateable : ResourcesBase.Resource) => {
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
};


/**
 * Update state from server: Fetch post pool, query it for all
 * ratings, and store and render them.  If a rating of the current
 * user exists, store and render that separately.
 *
 * FIXME: this function will have a much shorter implementation once
 * get search requests are available.
 */
export var updateRatings = (
    adapter : IRatingAdapter<any>,
    $scope : IRatingScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User
) : ng.IPromise<void> => {
    return postPoolPathPromise($scope, adhHttp)
        .then((postPoolPath) => adhHttp.get(postPoolPath))
        .then((postPool) => {
            var ratingPromises : ng.IPromise<ResourcesBase.Resource>[] =
                postPool.data["adhocracy.sheets.pool.IPool"].elements
                .map((index : number, path : string) => adhHttp.get(path));

            return $q.all(ratingPromises).then((ratings) => {
                resetRatings($scope);
                _.forOwn(ratings, (rating) => {

                    var checkValue = (rating, value : RatingValue) : boolean =>
                        adapter.value(rating) === value;

                    var iscurrentuser = (rating) : boolean =>
                        adapter.subject(rating) === adhUser.userPath;

                    if (checkValue(rating, RatingValue.pro)) {
                        $scope.ratings.pro += 1;
                    } else if (checkValue(rating, RatingValue.contra)) {
                        $scope.ratings.contra += 1;
                    } else if (checkValue(rating, RatingValue.neutral)) {
                        $scope.ratings.neutral += 1;
                    }

                    if (iscurrentuser(rating)) {
                        $scope.thisUsersRating = rating;
                    }
                });
            });
        });
};


/**
 * controller for rating widget.  promises a void in order to notify
 * the unit test suite that it is done setting up its state.  (the
 * widget will ignore this promise.)
 */
export var ratingController = (
    adapter : IRatingAdapter<any>,
    $scope : IRatingScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User
) : ng.IPromise<void> => {
    resetRatings($scope);
    return updateRatings(adapter, $scope, $q, adhHttp, adhUser);
};


export var createDirective = (
    adapter : IRatingAdapter<any>,
    $q : ng.IQService,
    adhConfig : AdhConfig.Type,
    adhPreliminaryNames : AdhPreliminaryNames
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Rating.html",
        scope: {
            refersTo: "@",
            postPoolSheet : "@",
            postPoolField : "@"
        },
        link: (scope : IRatingScope) => {
            scope.isActive = (rating : RatingValue) =>
                (typeof scope.thisUsersRating !== "undefined" &&
                 rating === adapter.value(scope.thisUsersRating)) ? "rating-button-active" : "";

            scope.cast = (rating : RatingValue) : void => {
                if (scope.isActive(rating)) {
                    // click on active button to un-rate

                    adapter.value(scope.thisUsersRating, <any>false);  // FIXME: we need to decide how we want to handle deletion!
                    scope.ratings[RatingValue[rating]] -= 1;
                    scope.postUpdate();
                } else {
                    // click on inactive button to (re-)rate

                    // increase new value
                    scope.ratings[RatingValue[rating]] += 1;

                    scope.assureUserRatingExists()
                        .then(() => {
                            // update thisUsersRating
                            adapter.value(scope.thisUsersRating, rating);

                            // decrease old value
                            scope.ratings[adapter.value(scope.thisUsersRating)] -= 1;

                            // send new rating to server
                            scope.postUpdate();
                        });
                }
            };

            scope.assureUserRatingExists = () : ng.IPromise<void> => {
                return $q.when(<any>undefined);
            };

            scope.postUpdate = () : ng.IPromise<void> => {
                return $q.when(<any>undefined);
            };
        },
        controller: ["$scope", "$q", "adhHttp", "adhUser", ($scope, $q, adhHttp, adhUser) =>
            ratingController(adapter, $scope, $q, adhHttp, adhUser)]
    };
};
