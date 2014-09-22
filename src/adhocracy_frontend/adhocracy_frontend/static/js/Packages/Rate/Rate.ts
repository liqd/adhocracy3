import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhHttp = require("../Http/Http");
import AdhResource = require("../../Resources");
import AdhUser = require("../User/User");
import Util = require("../Util/Util");

import ResourcesBase = require("../../ResourcesBase");

import RIRate = require("../../Resources_/adhocracy/resources/rate/IRate");
// import RIRateVersion = require("../../Resources_/adhocracy/resources/rate/IRateVersion");
// import SICanRate = require("../../Resources_/adhocracy/sheets/rate/ICanRate");
// import SIRate = require("../../Resources_/adhocracy/sheets/rate/IRate");
// import SIRateable = require("../../Resources_/adhocracy/sheets/rate/IRateable");

var pkgLocation = "/Rate";


export enum RateValue {
    contra = -1,
    neutral,
    pro
};


export interface IRateScope extends ng.IScope {
    refersTo : string;
    postPoolPath : string;
    postPoolSheet : string;
    postPoolField : string;
    rates : {
        pro : number;
        contra : number;
        neutral : number;
    };
    thisUsersRate : AdhResource.Content<any>;
    allRates : AdhResource.Content<any>[];
    isActive : (RateValue) => boolean;
    isActiveClass : (RateValue) => string;  // css class name if RateValue is active, or "" otherwise.
    toggleShowDetails() : void;
    cast(RateValue) : void;
    assureUserRateExists() : ng.IPromise<boolean>;
    postUpdate() : ng.IPromise<void>;
}


// (this type is over-restrictive in that T is used for both the
// rate, the subject, and the target.  luckily, subtype-polymorphism
// is too cool to complain about it here.  :-)
export interface IRateAdapter<T extends AdhResource.Content<any>> {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
    is(resource : T) : boolean;
    subject(resource : T) : string;
    subject(resource : T, value : string) : T;
    object(resource : T) : string;
    object(resource : T, value : string) : T;
    rate(resource : T) : RateValue;
    rate(resource : T, value : RateValue) : T;
    creator(resource : T) : string;
    creationDate(resource : T) : string;
    modificationDate(resource : T) : string;
}


/**
 * initialise rates
 */
export var resetRates = ($scope : IRateScope) : void => {
    $scope.rates = {
        pro: 0,
        contra: 0,
        neutral: 0
    };

    delete $scope.thisUsersRate;
};


/**
 * fetch post pool path with coordinates given in scope
 */
export var postPoolPathPromise = (
    $scope : IRateScope,
    adhHttp : AdhHttp.Service<any>
) : ng.IPromise<string> => {
    return adhHttp.get($scope.refersTo).then((rateable : ResourcesBase.Resource) => {
        if (rateable.hasOwnProperty("data")) {
            if (rateable.data.hasOwnProperty($scope.postPoolSheet)) {
                if (rateable.data[$scope.postPoolSheet].hasOwnProperty($scope.postPoolField)) {
                    $scope.postPoolPath = rateable.data[$scope.postPoolSheet][$scope.postPoolField];
                    return $scope.postPoolPath;
                }
            }
        }

        throw "post pool field in " + $scope.postPoolSheet + "/" + $scope.postPoolField +
            " not found in content type " + rateable.content_type;
    });
};


/**
 * Use postPoolPathPromise to fetch post pool path, then fetch the
 * post pool and all latest versions of the items contained in it.
 *
 * Promise an array of those versions.
 */
export var postPoolContentsPromise = (
    $scope : IRateScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>
) : ng.IPromise<RIRate[]> => {
    return postPoolPathPromise($scope, adhHttp)
        .then((postPoolPath) => adhHttp.get(postPoolPath))
        .then((postPool) => {
            var ratePromises : ng.IPromise<ResourcesBase.Resource>[] =
                postPool.data["adhocracy.sheets.pool.IPool"].elements
                    .map((path : string, index : number) =>
                        adhHttp
                           .getNewestVersionPathNoFork(Util.parentPath(path))
                           .then((path) => adhHttp.get(path)));

            return $q.all(ratePromises);
        });
};


/**
 * Update state from server: Fetch post pool, query it for all
 * rates, and store and render them.  If a rate of the current
 * user exists, store and render that separately.
 *
 * FIXME: this function will have a much shorter implementation once
 * get search requests are available.
 */
export var updateRates = (
    adapter : IRateAdapter<any>,
    $scope : IRateScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User
) : ng.IPromise<void> => {
    return postPoolContentsPromise($scope, $q, adhHttp)
        .then((rates) => {
            resetRates($scope);
            _.forOwn(rates, (rate) => {

                // FIXME: (summary of a conversation between mf and
                // joka on this) rateable post pools *should* just
                // contain ratings, but that's not the case at the
                // writing of these lines.  we add a little filter
                // condition here, but in the future, it should
                // probably be ok to trust the backend on this.
                if (!adapter.is(rate)) {
                    return;
                }

                // if this is a rating of another content object:
                // ignore.
                if (adapter.object(rate) !== $scope.refersTo) {
                    return;
                }

                var checkValue = (rate, value : RateValue) : boolean =>
                    adapter.rate(rate) === value;

                var iscurrentuser = (rate) : boolean =>
                    adapter.subject(rate) === adhUser.userPath;

                if (checkValue(rate, RateValue.pro)) {
                    $scope.rates.pro += 1;
                } else if (checkValue(rate, RateValue.contra)) {
                    $scope.rates.contra += 1;
                } else if (checkValue(rate, RateValue.neutral)) {
                    $scope.rates.neutral += 1;
                }

                if (iscurrentuser(rate)) {
                    $scope.thisUsersRate = rate;
                }
            });
        });
};


/**
 * controller for rate widget.  promises a void in order to notify
 * the unit test suite that it is done setting up its state.  (the
 * widget will ignore this promise.)
 */
export var rateController = (
    adapter : IRateAdapter<any>,
    $scope : IRateScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User,
    adhPreliminaryNames : AdhPreliminaryNames
) : ng.IPromise<void> => {

    $scope.isActive = (rate : RateValue) : boolean =>
        typeof $scope.thisUsersRate !== "undefined" &&
        rate === adapter.rate($scope.thisUsersRate);

    $scope.isActiveClass = (rate : RateValue) : string =>
        $scope.isActive(rate) ? "rate-button-active" : "";

    $scope.toggleShowDetails = () => {
        if (typeof $scope.allRates === "undefined") {
            $scope.allRates = [];
            postPoolContentsPromise($scope, $q, adhHttp)
                .then((rates) => {
                    $scope.allRates = rates;
                });
        } else {
            delete $scope.allRates;
        }
    }

    $scope.cast = (rate : RateValue) : void => {
        if (!adhUser.userPath) {
            // if user is not logged in, rating silently refuses to work.
            return;
        }

        if ($scope.isActive(rate)) {
            // click on active button to un-rate

            /*

              (the current implementation does not allow withdrawing
              of rates, so if you click on "pro" twice in a row, the
              second time will have no effect.  the work-around is for
              the user to rate something "neutral".  a proper fixed
              will be provided later.)

              adapter.rate($scope.thisUsersRate, <any>false);
              $scope.rates[RateValue[rate]] -= 1;
              $scope.postUpdate();

            */
        } else {
            // click on inactive button to (re-)rate

            $scope.assureUserRateExists()
                .then((didExistBefore) => {
                    if (didExistBefore) {
                        // decrease old value
                        $scope.rates[adapter.rate($scope.thisUsersRate)] -= 1;
                    }

                    if ((!didExistBefore) || (<any>$scope.thisUsersRate).rate === rate) {
                        // set new value
                        adapter.rate($scope.thisUsersRate, rate);
                        $scope.rates[rate] += 1;

                        // send new rate to server
                        $scope.postUpdate();
                    }
                });
        }
    };

    $scope.assureUserRateExists = () : ng.IPromise<boolean> => {
        if (typeof $scope.thisUsersRate !== "undefined") {
            return $q.when(true);
        } else {
            return adhHttp
                .withTransaction((transaction) : ng.IPromise<boolean> => {
                    var item : AdhHttp.ITransactionResult =
                        transaction.post($scope.postPoolPath, new RIRate({ preliminaryNames: adhPreliminaryNames }));
                    var version : AdhHttp.ITransactionResult =
                        transaction.get(item.first_version_path);

                    return transaction.commit()
                        .then((responses) : boolean => {
                            $scope.thisUsersRate = responses[version.index];
                            adapter.subject($scope.thisUsersRate, adhUser.userPath);
                            adapter.object($scope.thisUsersRate, $scope.refersTo);
                            return false;
                        });
                });
        }
    };

    $scope.postUpdate = () : ng.IPromise<void> => {
        if (typeof $scope.thisUsersRate === "undefined") {
            throw "internal error?!";
        } else {
            return adhHttp
                .postNewVersionNoFork($scope.thisUsersRate.path, $scope.thisUsersRate)
                .then((response : { value: RIRate }) => {
                    $scope.thisUsersRate = response.value;
                });
        }
    };

    resetRates($scope);
    return updateRates(adapter, $scope, $q, adhHttp, adhUser);
};


export var createDirective = (
    adapter : IRateAdapter<any>,
    adhConfig : AdhConfig.Type
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Rate.html",
        scope: {
            refersTo: "@",
            postPoolSheet : "@",
            postPoolField : "@"
        },
        controller: ["$scope", "$q", "adhHttp", "adhUser", "adhPreliminaryNames", ($scope, $q, adhHttp, adhUser, adhPreliminaryNames) =>
            rateController(adapter, $scope, $q, adhHttp, adhUser, adhPreliminaryNames)]
    };
};
