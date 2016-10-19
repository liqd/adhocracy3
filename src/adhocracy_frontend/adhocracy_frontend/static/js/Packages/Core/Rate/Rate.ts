import * as _ from "lodash";

import * as AdhAnonymize from "../Anonymize/Anonymize";
import * as AdhConfig from "../Config/Config";
import * as AdhCredentials from "../User/Credentials";
import * as AdhEventManager from "../EventManager/EventManager";
import * as AdhHttp from "../Http/Http";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";
import * as AdhResourceArea from "../ResourceArea/ResourceArea";
import * as AdhResourceUtil from "../Util/ResourceUtil";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUser from "../User/User";
import * as AdhUtil from "../Util/Util";
import * as AdhWebSocket from "../WebSocket/WebSocket";

import * as ResourcesBase from "../../ResourcesBase";

import RIRate from "../../../Resources_/adhocracy_core/resources/rate/IRate";
import RIRateVersion from "../../../Resources_/adhocracy_core/resources/rate/IRateVersion";
import * as SIPool from "../../../Resources_/adhocracy_core/sheets/pool/IPool";
import * as SIRate from "../../../Resources_/adhocracy_core/sheets/rate/IRate";
import * as SIUserBasic from "../../../Resources_/adhocracy_core/sheets/principal/IUserBasic";
import * as SIWorkflow from "../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";

var pkgLocation = "/Core/Rate";


/**
 * Generic rate directive
 *
 * This module provides a generic code for rate widgets. It is generic in that
 * it can be used with different sheets and templates.
 *
 * FIXME: The code is currently tied to RIRateVersion
 *
 * An interesting detail is that the rate item is only created on the server
 * when a user casts a rate for the first time.  This does pose a special
 * challange for keeping multiple rate directives on the same page in sync
 * because there is no resource on the server that we could register
 * websockets on.  For this reason, there is the adhRateEventManager service
 * that is used to sync these directives locally.
 */


export interface IRateScope extends angular.IScope {
    refersTo : string;
    showResults : string;
    disabled : boolean;
    myRate : number;
    rates(rate : number) : number;
    optionsPostPool : AdhHttp.IOptions;
    ready : boolean;
    hasCast : boolean;

    cast(value : number) : angular.IPromise<void>;
    uncast() : angular.IPromise<void>;
    toggle(value : number) : angular.IPromise<void>;
    showResult() : boolean;
    showResultToggle() : boolean;
    toggleShowResult() : void;

    // not currently used in the UI
    auditTrail : { subject: string; rate: number }[];
    auditTrailVisible : boolean;
    toggleShowDetails() : void;
}


/**
 * promise workflow state.
 */
export var getWorkflowState = (
    adhResourceArea : AdhResourceArea.Service
) => (resourceUrl : string) : angular.IPromise<string> => {
    return adhResourceArea.getProcess(resourceUrl, false).then((resource : ResourcesBase.IResource) => {
        if (typeof resource !== "undefined") {
            var workflowSheet = resource.data[SIWorkflow.nick];
            if (typeof workflowSheet !== "undefined") {
                return workflowSheet.workflow_state;
            }
        }
    });
};


export class Service {
    constructor(
        private $q : angular.IQService,
        private adhHttp : AdhHttp.Service
    ) {}

    /**
     * Promise rate of specified subject.  Reject if none could be found.
     *
     * NOTE: This will return the first match. The backend must make sure that
     * there is never more than one rate item per subject-object pair.
     */
    public fetchRate(poolPath : string, object : string, subject : string) : angular.IPromise<RIRateVersion> {
        var query : any = {
            elements: "paths",
            content_type: RIRateVersion.content_type,
            depth: "all",
            tag: "LAST"
        };
        query[SIRate.nick + ":subject"] = subject;
        query[SIRate.nick + ":object"] = object;
        return this.adhHttp.get(poolPath, query).then((pool) => {
            if (pool.data[SIPool.nick].elements.length > 0) {
                return this.adhHttp.get(pool.data[SIPool.nick].elements[0]);
            } else {
                return this.$q.reject("Not Found");
            }
        });
    }

    /**
     * Promise aggregates rates of all users.
     */
    public fetchAggregatedRates(poolPath : string, object : string) : angular.IPromise<{[key : string]: number}> {
        var query : any = {
            content_type: RIRateVersion.content_type,
            depth: "all",
            tag: "LAST",
            aggregateby: "rate"
        };
        query[SIRate.nick + ":object"] = object;

        return this.adhHttp.get(poolPath, query).then((pool) => {
            return pool.data[SIPool.nick].aggregateby.rate;
        });
    }
}


export var directiveFactory = (template : string, sheetName : string) => (
    $q : angular.IQService,
    adhRate : Service,
    adhRateEventManager : AdhEventManager.EventManager,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhWebSocket : AdhWebSocket.Service,
    adhPermissions : AdhPermissions.Service,
    adhCredentials : AdhCredentials.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceArea : AdhResourceArea.Service,
    adhUser : AdhUser.Service,
    adhDone
) => {
    "use strict";

    var getAnonymizeInfo = AdhAnonymize.getAnonymizeInfo(adhConfig, adhHttp, adhUser, $q);

    /**
     * Collect detailed information about poolPath specific to ratings for object.
     */
    var fetchAuditTrail = (poolPath : string, object : string) : angular.IPromise<any> => {
        var query : any = {
            content_type: RIRateVersion.content_type,
            depth: 2,
            tag: "LAST"
        };
        query[SIRate.nick + ":object"] = object;

        return adhHttp.get(poolPath, query)
            .then((poolRsp) => {
                var ratePaths : string[] = poolRsp.data[SIPool.nick].elements;
                var rates : ResourcesBase.IResource[] = [];
                var users : ResourcesBase.IResource[] = [];
                var auditTrail : { subject: string; rate: number }[] = [];

                adhHttp.withTransaction((transaction) : angular.IPromise<void> => {
                    var gets : AdhHttp.ITransactionResult[] = ratePaths.map((path) => transaction.get(path));

                    return transaction.commit()
                        .then((responses) => {
                            gets.map((transactionResult) => {
                                rates.push(<any>responses[transactionResult.index]);
                            });
                        });
                }).then(() => {
                    return adhHttp.withTransaction((transaction) : angular.IPromise<void> => {
                        var gets : AdhHttp.ITransactionResult[] = rates.map((rate) => {
                            return transaction.get(rate.data[SIRate.nick].subject);
                        });

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
                            subject: users[ix].data[SIUserBasic.nick].name,
                            rate: parseInt(rates[ix].data[SIRate.nick].rate, 10)
                        };
                    });
                    return auditTrail;
                });
            });
    };

    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + template,
        scope: {
            refersTo: "@",
            showResults: "@",
            disabled: "="
        },
        link: (scope : IRateScope) : void => {
            var myRateResource : ResourcesBase.IResource;
            var webSocketOff : () => void;
            var postPoolPath : string;
            var rates : {[key : string]: number};
            var lock : boolean;
            var storeMyRateResource : (resource : ResourcesBase.IResource) => void;
            var forceResult : boolean = false;

            var updateMyRate = () : angular.IPromise<void> => {
                if (adhCredentials.loggedIn) {
                    return adhRate.fetchRate(postPoolPath, scope.refersTo, adhCredentials.userPath).then((resource) => {
                        storeMyRateResource(resource);
                        scope.myRate = parseInt(resource.data[SIRate.nick].rate, 10);
                        scope.hasCast = true;
                    }, () => undefined);
                } else {
                    return $q.when();
                }
            };

            var updateAggregatedRates = () : angular.IPromise<void> => {
                return adhRate.fetchAggregatedRates(postPoolPath, scope.refersTo).then((r) => {
                    rates = r;
                });
            };

            var updateAuditTrail = () : angular.IPromise<void> => {
                return fetchAuditTrail(postPoolPath, scope.refersTo).then((auditTrail)  => {
                    scope.auditTrail = auditTrail;
                });
            };

            var assureUserRateExists = () : angular.IPromise<RIRateVersion> => {
                if (typeof myRateResource !== "undefined") {
                    return $q.when(myRateResource);
                } else {
                    return getAnonymizeInfo(postPoolPath, "POST").then((anonymizeInfo) => {
                        return adhHttp.withTransaction((transaction) => {
                            var item = transaction.post(postPoolPath, {
                                path: adhPreliminaryNames.nextPreliminary(),
                                first_version_path: adhPreliminaryNames.nextPreliminary(),
                                content_type: RIRate.content_type,
                                data: {},
                            });
                            var version = transaction.get(item.first_version_path);

                            return transaction.commit({ anonymize : anonymizeInfo.defaultValue })
                                .then((responses) => {
                                    storeMyRateResource(<RIRateVersion>responses[version.index]);
                                    return myRateResource;
                                });
                        });
                    });
                }
            };

            storeMyRateResource = (resource : ResourcesBase.IResource) => {
                myRateResource = resource;

                if (typeof webSocketOff === "undefined") {
                    var itemPath = AdhUtil.parentPath(resource.path);
                    webSocketOff = adhWebSocket.register(itemPath, (message) => {
                        updateMyRate();
                        updateAggregatedRates();
                    });
                    scope.$on("$destroy", webSocketOff);
                }
            };

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

            scope.rates = (rate : number) : number => {
                return rates[rate.toString()] || 0;
            };

            // NOTE: In the future we might want to delete the rate instead.
            // For now, uncasting is simply implemented by casting a "neutral" rate.
            scope.uncast = () : angular.IPromise<void> => {
                return scope.cast(0);
            };

            scope.cast = (rate : number) : angular.IPromise<void> => {
                if (lock) {
                    return $q.reject("locked");
                }

                if (!scope.optionsPostPool.POST) {
                    if (!adhCredentials.loggedIn) {
                        adhTopLevelState.setCameFromAndGo("/login");
                    } else {
                        // FIXME
                    }
                    return $q.reject("Permission Error");
                } else {
                    lock = true;

                    return assureUserRateExists().then((version) => {
                        var newVersion = AdhResourceUtil.derive(version, {
                            preliminaryNames: adhPreliminaryNames
                        });

                        newVersion.data[SIRate.nick].rate = rate;
                        newVersion.data[SIRate.nick].object = scope.refersTo;
                        newVersion.data[SIRate.nick].subject = adhCredentials.userPath;

                        return getAnonymizeInfo(AdhUtil.parentPath(version.path), "POST").then((anonymizeInfo) => {
                            return adhHttp.postNewVersionNoFork(version.path, newVersion, [], { anonymize: anonymizeInfo.defaultValue })
                                .then(() => {
                                    adhRateEventManager.trigger(scope.refersTo);
                                    scope.auditTrailVisible = false;
                                    return $q.all([updateMyRate(), updateAggregatedRates()]);
                                })
                                .then(() => undefined);
                        });
                    }).finally(() => {
                        lock = false;
                    });
                }
            };

            scope.toggle = (rate : number) : angular.IPromise<void> => {
                if (rate === scope.myRate) {
                    return scope.uncast();
                } else {
                    return scope.cast(rate);
                }
            };

            var showResult : boolean = false;

            scope.showResult = () : boolean => {
                if (scope.showResultToggle()) {
                    return showResult;
                } else {
                    return true;
                }
            };

            scope.showResultToggle = () : boolean => {
                return !scope.hasCast && !forceResult;
            };

            scope.toggleShowResult = () : void => {
                showResult = !showResult;
            };

            // sync with other local rate buttons
            scope.$on("$destroy", adhRateEventManager.on(scope.refersTo, () => {
                updateMyRate();
                updateAggregatedRates();
            }));

            scope.auditTrailVisible = false;
            adhHttp.get(scope.refersTo)
                .then((rateable) => {
                    postPoolPath = rateable.data[sheetName].post_pool;
                })
                .then(() => $q.all([updateMyRate(), updateAggregatedRates()]))
                .then(() => {
                    adhPermissions.bindScope(scope, postPoolPath, "optionsPostPool");
                    scope.ready = true;
                    adhDone();
                });

            getWorkflowState(adhResourceArea)(scope.refersTo)
                .then((workflowState : string) => {
                    if (workflowState === "result") {
                        forceResult = true;
                    }
                });
        }
    };
};
