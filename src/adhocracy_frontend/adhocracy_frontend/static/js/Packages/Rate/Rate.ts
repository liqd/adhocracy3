import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPermissions = require("../Permissions/Permissions");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUser = require("../User/User");

import ResourcesBase = require("../../ResourcesBase");

import RIRate = require("../../Resources_/adhocracy_core/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy_core/resources/rate/IRateVersion");
import RIUser = require("../../Resources_/adhocracy_core/resources/principal/IUser");
import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");
import SIRate = require("../../Resources_/adhocracy_core/sheets/rate/IRate");
import SIUserBasic = require("../../Resources_/adhocracy_core/sheets/principal/IUserBasic");

import Adapter = require("./Adapter");

var pkgLocation = "/Rate";


/**
 * Motivation and UI
 * ~~~~~~~~~~~~~~~~~
 *
 * The UI should show the rating button as follows::
 *
 *     Count:  Pros  Cons  Neutrals
 *      +13    14    1     118
 *
 * The words "Props", "Cons", Neutrals" are buttons.  If the user clicks
 * on any one, it becomes active, and all other buttons become inactive.
 * Initially, all buttons are inactive.
 *
 * The current design: Once any of the buttons is activated, the rating
 * cannot be taken back.  The user can only click on "neutral" if she
 * wants to change her mind about having an opinion.
 *
 * The final design: if an active button is clicked, it becomes inactive,
 * and the rating object will be deleted.  (FIXME: This requires a
 * deletion semantics, which should also become a section in this
 * document.)
 */


export interface IRateScope extends ng.IScope {
    refersTo : string;
    rates(rate : number) : number;
    allRateResources : RIRateVersion[];
    auditTrail : { subject: string; rate: number }[];
    auditTrailVisible : boolean;
    isActive : (value : number) => boolean;
    toggleShowDetails() : void;
    cast(value : number) : void;
    toggle() : void;
    postUpdate() : ng.IPromise<void>;
    optionsPostPool : AdhHttp.IOptions;
    ready : boolean;
}


// (this type is over-restrictive in that T is used for both the
// rate, the subject, and the target.  luckily, subtype-polymorphism
// is too cool to complain about it here.  :-)
export interface IRateAdapter<T extends ResourcesBase.Resource> {
    create(settings : any) : T;
    createItem(settings : any) : any;
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


// FIXME: This is currently not generic but tied to RIRateVersion
export var directiveFactory = (template : string, adapter : IRateAdapter<RIRateVersion>) => (
    $q : ng.IQService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    adhUser : AdhUser.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhDone
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + template,
        scope: {
            refersTo: "@",
            postPoolSheet : "@",
            postPoolField : "@"
        },
        link: (scope : IRateScope) : void => {
            var myRateResource : RIRateVersion;
            var postPoolPath : string;
            var rates : {[key : string]: number};

            /**
             * Promise rate of specified subject.  Reject if none could be found.
             *
             * NOTE: This will return the first match. The backend must make sure that
             * there is never more than one rate item per subject-object pair.
             */
            var fetchRate = (poolPath : string, object : string, subject : string) : ng.IPromise<RIRateVersion> => {
                var query : any = {
                    content_type: RIRateVersion.content_type,
                    depth: 2,
                    tag: "LAST"
                };
                query[SIRate.nick + ":subject"] = subject;
                query[SIRate.nick + ":object"] = object;

                return adhHttp.get(poolPath, query).then((pool) => {
                    if (pool.data[SIPool.nick].elements.length > 0) {
                        return adhHttp.get(pool.data[SIPool.nick].elements[0]);
                    } else {
                        return $q.reject("Not Found");
                    }
                });
            };

            var updateMyRate = () : ng.IPromise<void> => {
                return fetchRate(postPoolPath, scope.refersTo, adhUser.userPath).then((rate) => {
                    myRateResource = rate;
                });
            };

            /**
             * Promise aggregates rates of all users.
             */
            var fetchAggregatedRates = (poolPath : string, object : string) : ng.IPromise<{[key : string]: number}> => {
                var query : any = {
                    content_type: RIRateVersion.content_type,
                    depth: 2,
                    tag: "LAST",
                    count: "true",
                    aggregateby: "rate"
                };
                query[SIRate.nick + ":object"] = object;

                return adhHttp.get(poolPath, query).then((pool) => {
                    return pool.data[SIPool.nick].aggregateby.rate;
                });
            };

            var updateAggregatedRates = () : ng.IPromise<void> => {
                return fetchAggregatedRates(postPoolPath, scope.refersTo).then((r) => {
                    rates = r;
                });
            };

            /**
             * Collect detailed information about poolPath specific to ratings for object.
             */
            var fetchAuditTrail = (poolPath : string, object : string) : ng.IPromise<any> => {
                var query : any = {
                    content_type: RIRateVersion.content_type,
                    depth: 2,
                    tag: "LAST"
                };
                query[SIRate.nick + ":object"] = object;

                return adhHttp.get(poolPath, query)
                    .then((poolRsp) => {
                        var ratePaths : string[] = poolRsp.data[SIPool.nick].elements;
                        var rates : RIRateVersion[] = [];
                        var users : RIUser[] = [];
                        var auditTrail : { subject: string; rate: number }[] = [];

                        adhHttp.withTransaction((transaction) : ng.IPromise<void> => {
                            var gets : AdhHttp.ITransactionResult[] = ratePaths.map((path) => transaction.get(path));

                            return transaction.commit()
                                .then((responses) => {
                                    gets.map((transactionResult) => {
                                        rates.push(<any>responses[transactionResult.index]);
                                    });
                                });
                        }).then(() => {
                            return adhHttp.withTransaction((transaction) : ng.IPromise<void> => {
                                var gets : AdhHttp.ITransactionResult[] = rates.map((rate) => transaction.get(adapter.subject(rate)));

                                return transaction.commit()
                                    .then((responses) => {
                                        gets.map((transactionResult) => {
                                            users.push(<any>responses[transactionResult.index]);
                                        });
                                    });
                            });
                        }).then(() => {
                            _.forOwn(ratePaths, (ratePath, ix) => {
                                auditTrail[ix] = {
                                    subject: users[ix].data[SIUserBasic.nick].name,  // (use adapter for user, too?)
                                    rate: adapter.rate(rates[ix])
                                };
                            });
                            return auditTrail;
                        });
                    });
            };

            var updateAuditTrail = () : ng.IPromise<void> => {
                return fetchAuditTrail(postPoolPath, scope.refersTo).then((auditTrail)  => {
                    scope.auditTrail = auditTrail;
                });
            };

            var assureUserRateExists = () : ng.IPromise<void> => {
                if (typeof myRateResource !== "undefined") {
                    return $q.when();
                } else {
                    return adhHttp
                        .withTransaction((transaction) : ng.IPromise<void> => {
                            var item : AdhHttp.ITransactionResult =
                                transaction.post(postPoolPath, new RIRate({ preliminaryNames: adhPreliminaryNames }));
                            var version : AdhHttp.ITransactionResult =
                                transaction.get(item.first_version_path);

                            return transaction.commit()
                                .then((responses) : void => {
                                    myRateResource = <RIRateVersion>responses[version.index];
                                    adapter.subject(myRateResource, adhUser.userPath);
                                    adapter.object(myRateResource, scope.refersTo);
                                });
                        });
                }
            };

            scope.isActive = (rate : number) : boolean =>
                typeof myRateResource !== "undefined" &&
                    rate === adapter.rate(myRateResource);

            scope.toggleShowDetails = () => {
                if (scope.auditTrailVisible) {
                    scope.auditTrailVisible = false;
                    delete scope.auditTrail;
                } else {
                    $q.all([updateMyRate(), updateAggregatedRates(), updateAuditTrail()]).then(() => {
                        scope.auditTrailVisible = true;
                    });
                }
            };

            /**
             * the current implementation does not allow withdrawing of
             * rates, so if you click on "pro" twice in a row, the second time
             * will have no effect.  the work-around is for the user to rate
             * something "neutral".  an alternative behavior is cast_toggle
             * defined below.
             */
            /*
            var castSimple = (rate : number) : void => {
                if (!scope.isActive(rate)) {
                    assureUserRateExists()
                        .then(() => {
                            adapter.rate(myRateResource, rate);
                            scope.postUpdate();
                        });
                }
            };
            */

            scope.rates = (rate : number) : number => {
                return rates[rate.toString()] || 0;
            };

            /**
             * if the design has no neutral button, un-upping can be
             * implemented as changeing the vote to 'neutral'.  this requires
             * the total votes count to disregard neutral votes in its filter
             * query, and has negative implications on backend performance,
             * but it works.
             */
            var castToggle = (rate : number) : void => {
                assureUserRateExists()
                    .then(() => {
                        var oldRate : number = myRateResource.data[SIRate.nick].rate;

                        if (rate !== 0 && oldRate === rate) {
                            rate = 0;
                        }
                        adapter.rate(myRateResource, rate);
                        scope.postUpdate();
                    });
            };

            scope.cast = (rate : number) : void => {
                if (!scope.optionsPostPool.POST) {
                    adhTopLevelState.redirectToLogin();
                }
                castToggle(rate);
            };


            scope.toggle = () : void => {
                if (scope.isActive(1)) {
                    scope.cast(0);
                } else {
                    scope.cast(1);
                }
            };

            scope.postUpdate = () : ng.IPromise<void> => {
                if (typeof myRateResource === "undefined") {
                    throw "internal error?!";
                } else {
                    return adhHttp
                        .postNewVersionNoFork(myRateResource.path, myRateResource)
                        .then((response : { value: RIRate }) => {
                            scope.auditTrailVisible = false;
                            return $q.all([updateMyRate(), updateAggregatedRates()]);
                        })
                        .then(() => { return; });
                }
            };

            scope.auditTrailVisible = false;
            adhHttp.get(scope.refersTo)
                .then((rateable) => {
                    postPoolPath = adapter.rateablePostPoolPath(rateable);
                })
                .then(() => $q.all([updateMyRate(), updateAggregatedRates()]))
                .then(() => {
                    adhPermissions.bindScope(scope, postPoolPath, "optionsPostPool");
                    scope.ready = true;
                    adhDone();
                });
        }
    };
};


export var moduleName = "adhRate";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhPermissions.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhTopLevelState.moduleName,
            AdhUser.moduleName
        ])
        .directive("adhRate", [
            "$q",
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhUser",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhDone",
            directiveFactory("/Rate.html", new Adapter.RateAdapter())])
        .directive("adhLike", [
            "$q",
            "adhConfig",
            "adhHttp",
            "adhPermissions",
            "adhUser",
            "adhPreliminaryNames",
            "adhTopLevelState",
            "adhDone",
            directiveFactory("/Like.html", new Adapter.RateAdapter())]);
};
