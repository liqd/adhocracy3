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
    pro,
    contra,
    neutral
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
    thisUsersRate : any;  // resource matching IRateAdapter (this is tricky to type, so we leave it blank for now.)
    isActive : (RateValue) => string;  // css class name if RateValue is active, or "" otherwise.
    cast(RateValue) : void;
    assureUserRateExists() : ng.IPromise<void>;
    postUpdate() : ng.IPromise<void>;
}


// (this type is over-restrictive in that T is used for both the
// rate, the subject, and the target.  luckily, subtype-polymorphism
// is too cool to complain about it here.  :-)
export interface IRateAdapter<T extends AdhResource.Content<any>> {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
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
    return postPoolPathPromise($scope, adhHttp)
        .then((postPoolPath) => adhHttp.get(postPoolPath))
        .then((postPool) => {
            var ratePromises : ng.IPromise<ResourcesBase.Resource>[] =
                postPool.data["adhocracy.sheets.pool.IPool"].elements
                    .map((path : string, index : number) =>
                        adhHttp
                           .getNewestVersionPath(Util.parentPath(path))
                           .then(adhHttp.get));

            return $q.all(ratePromises).then((rates) => {
                resetRates($scope);
                _.forOwn(rates, (rate) => {

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

    $scope.isActive = (rate : RateValue) =>
        (typeof $scope.thisUsersRate !== "undefined" &&
         rate === adapter.rate($scope.thisUsersRate)) ? "rate-button-active" : "";

    $scope.cast = (rate : RateValue) : void => {
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

            // increase new value
            $scope.rates[RateValue[rate]] += 1;

            $scope.assureUserRateExists()
                .then(() => {
                    // update thisUsersRate
                    adapter.rate($scope.thisUsersRate, rate);

                    // decrease old value
                    $scope.rates[adapter.rate($scope.thisUsersRate)] -= 1;

                    // send new rate to server
                    $scope.postUpdate();
                });
        }
    };

    $scope.assureUserRateExists = () : ng.IPromise<void> => {
        if (typeof $scope.thisUsersRate !== "undefined") {
            return $q.when();
        } else {
            return adhHttp
                .withTransaction((transaction) : ng.IPromise<void> => {
                    var item : AdhHttp.ITransactionResult =
                        transaction.post($scope.postPoolPath, new RIRate({ preliminaryNames: adhPreliminaryNames }));
                    var version : AdhHttp.ITransactionResult =
                        transaction.get(item.first_version_path);

                    return transaction.commit()
                        .then((responses) : void => {
                            $scope.thisUsersRate = responses[version.index];
                        });
                });
        }
    };

    $scope.postUpdate = () : ng.IPromise<void> => {
        if (typeof $scope.thisUsersRate !== "undefined") {
            throw "internal error";
        } else {
            return adhHttp
                .postNewVersion(Util.parentPath($scope.thisUsersRate), $scope.thisUsersRate)
                .then((response : RIRate) => {
                    $scope.thisUsersRate = response;
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
