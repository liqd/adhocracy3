import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhHttp = require("../Http/Http");
import AdhResource = require("../../Resources");
import AdhUser = require("../User/User");

import ResourcesBase = require("../../ResourcesBase");

import RIRate = require("../../Resources_/adhocracy/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy/resources/rate/IRateVersion");
// import SICanRate = require("../../Resources_/adhocracy/sheets/rate/ICanRate");
// import SIRate = require("../../Resources_/adhocracy/sheets/rate/IRate");
// import SIRateable = require("../../Resources_/adhocracy/sheets/rate/IRateable");

var pkgLocation = "/Rate";


export interface IRateScope extends ng.IScope {
    refersTo : string;
    postPoolPath : string;
    rates : {
        pro : number;
        contra : number;
        neutral : number;
    };
    thisUsersRate : AdhResource.Content<any>;
    allRates : { subject: string; rate: number }[];
    isActive : (value : number) => boolean;
    isActiveClass : (value : number) => string;  // css class name if RateValue is active, or "" otherwise.
    toggleShowDetails() : void;
    cast(value : number) : void;
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
    isRate(resource : T) : boolean;
    isRateable(resource : T) : boolean;
    rateablePostPoolPath(resource : T) : string;
    subject(resource : T) : string;
    subject(resource : T, value : string) : T;
    object(resource : T) : string;
    object(resource : T, value : string) : T;
    rate(resource : T) : number;
    rate(resource : T, value : number) : T;
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



// FIXME: updateRates on postUpdate; updateRates on toggleBla; eliminate manual aggr. maintenance.



/**
 * add number to pro / contra / neutral count.
 */
export var addToRateCount = ($scope : IRateScope, rate : number, delta : number) : void => {
    switch (rate) {
        case 1: {
            $scope.rates.pro += delta;
            break;
        }
        case -1: {
            $scope.rates.contra += delta;
            break;
        }
        case 0: {
            $scope.rates.neutral += delta;
            break;
        }
        default: {
            throw "unknown rate value: " + rate.toString();
        }
    }
};


/**
 * Take the rateable in $scope.refersTo and collect all ratings that
 * rate this resource from its post pool.  Promise an array of latest
 * rating versions.
 *
 * FIXME: make better use of the query filter api.
 */
export var fetchAllRates = (
    adapter : IRateAdapter<any>,
    $scope : IRateScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>
) : ng.IPromise<RIRateVersion[]> => {
    return adhHttp
        .get($scope.refersTo).then((rateable : ResourcesBase.Resource) => {
            $scope.postPoolPath = adapter.rateablePostPoolPath(rateable);
            return $scope.postPoolPath;
        })
        .then((postPoolPath) => adhHttp.get(postPoolPath, {
            content_type: "adhocracy.resources.rate.IRate"
        }))
        .then((postPool) => {
            var ratePromises : ng.IPromise<ResourcesBase.Resource>[] =
                postPool.data["adhocracy.sheets.pool.IPool"].elements
                    .map((path : string, index : number) =>
                        adhHttp
                           .getNewestVersionPathNoFork(path)
                           .then((path) => adhHttp.get(path)));

            var hasMatchingRefersTo = (rate) =>
                adapter.object(rate) === $scope.refersTo;

            return $q.all(ratePromises)
                .then((rates) => _.filter(rates, hasMatchingRefersTo));
        });
};


/**
 * Update state from server: Fetch post pool, query it for all
 * rates, and store and render them.  If a rate of the current
 * user exists, store and render that separately.
 */
export var updateRates = (
    adapter : IRateAdapter<any>,
    $scope : IRateScope,
    $q : ng.IQService,
    adhHttp : AdhHttp.Service<any>,
    adhUser : AdhUser.User
) : ng.IPromise<void> => {
    return fetchAllRates(adapter, $scope, $q, adhHttp)
        .then((rates) => {
            resetRates($scope);
            _.forOwn(rates, (rate) => {
                addToRateCount($scope, adapter.rate(rate), 1);

                if (adapter.subject(rate) === adhUser.userPath) {
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

    $scope.isActive = (rate : number) : boolean =>
        typeof $scope.thisUsersRate !== "undefined" &&
            rate === adapter.rate($scope.thisUsersRate);

    $scope.isActiveClass = (rate : number) : string =>
        $scope.isActive(rate) ? "is-rate-button-active" : "";

    // FIXME: if we were using web sockets, this would be done quite
    // differently.  toggleShowDetails should just toggle some
    // visibility flag, while $scope.allRates would be kept in sync
    // with the backend elsewhere.
    $scope.toggleShowDetails = () => {
        if (typeof $scope.allRates === "undefined") {
            $scope.allRates = [];
            fetchAllRates(adapter, $scope, $q, adhHttp)
                .then((rates) => {
                    var promises : ng.IPromise<{ subject : string; rate : number }>[] = rates.map((rate) => {
                        return adhHttp.get(adapter.subject(rate)).then((user) => {
                            return {
                                subject: user.data["adhocracy.sheets.user.IUserBasic"].name,
                                // FIXME: use adapter?  (which one?)
                                rate: adapter.rate(rate)
                            };
                        });
                    });

                    $q.all(promises).then((renderables) => {
                        $scope.allRates = renderables;
                    });
                });
        } else {
            delete $scope.allRates;
        }
    };

    $scope.cast = (rate : number) : void => {
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
                    delete $scope.allRates;

                    if (didExistBefore) {
                        // decrease old value
                        addToRateCount($scope, adapter.rate($scope.thisUsersRate), -1);
                    }

                    // set new value
                    adapter.rate($scope.thisUsersRate, rate);
                    addToRateCount($scope, rate, 1);

                    // send new rate to server
                    $scope.postUpdate();
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
                    return adhHttp.get(response.value.path)
                        .then((response : RIRate) => {
                            $scope.thisUsersRate = response;
                            return;
                        });
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
