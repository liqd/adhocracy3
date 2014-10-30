import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhInject = require("../Inject/Inject");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

import ResourcesBase = require("../../ResourcesBase");

import RIMercatorProposal = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposal");
import RIMercatorProposalVersion = require("../../Resources_/adhocracy_mercator/resources/mercator/IMercatorProposalVersion");
import SIDetails = require("../../Resources_/adhocracy_mercator/sheets/mercator/IDetails");
import SIExtras = require("../../Resources_/adhocracy_mercator/sheets/mercator/IExtras");
import SIFinance = require("../../Resources_/adhocracy_mercator/sheets/mercator/IFinance");
import SIIntroduction = require("../../Resources_/adhocracy_mercator/sheets/mercator/IIntroduction");
import SIMetadata = require("../../Resources_/adhocracy_core/sheets/metadata/IMetadata");
import SIMotivation = require("../../Resources_/adhocracy_mercator/sheets/mercator/IMotivation");
import SIName = require("../../Resources_/adhocracy_core/sheets/name/IName");
import SIOrganizationInfo = require("../../Resources_/adhocracy_mercator/sheets/mercator/IOrganizationInfo");
import SIUserInfo = require("../../Resources_/adhocracy_mercator/sheets/mercator/IUserInfo");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

var pkgLocation = "/MercatorProposal";


export interface IScope extends AdhResourceWidgets.IResourceWidgetScope {
    poolPath : string;
    data : {
        basic : {
            user : {
                name : string;
                lastname : string;
                email : string;
            };
            organisation : {
                name : string;
                email : string;
                address : string;
                postcode : string;
                city : string;
                country : string;
                status : string;
                statustext : string;
                description : string;
                size : string;
                cooperation : boolean;
                cooperationText? : string;
            };
        };
        introduction : {
            title : string;
            teaser : string;
            picture? : any;
        };
        detail : {
            description : string;
            location : string;
            story : string;
        };
        motivation : {
            outcome : string;
            steps : string;
            value : string;
            partners : string;
        };
        finance : {
            budget : number;
            funding : number;
            granted : boolean;
            document? : any;
        };
        extra : {
            mediaFiles? : any[];
            experience? : string;
            hear : {
                colleague : boolean;
                website : boolean;
                newsletter : boolean;
                facebook : boolean;
                other : boolean;
                otherDescription : string;
            }
        };
    };
}


export class Widget<R extends ResourcesBase.Resource> extends AdhResourceWidgets.ResourceWidget<R, IScope> {
    constructor(
        adhConfig : AdhConfig.IService,
        adhHttp : AdhHttp.Service<any>,
        adhPreliminaryNames : AdhPreliminaryNames.Service,
        $q : ng.IQService
    ) {
        super(adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/ListItem.html";
    }

    public createDirective() : ng.IDirective {
        var directive = super.createDirective();
        directive.scope.poolPath = "@";
        return directive;
    }

    public _handleDelete(
        instance : AdhResourceWidgets.IResourceWidgetInstance<R, IScope>,
        path : string
    ) : ng.IPromise<void> {
        return this.$q.when();
    }

    private initializeScope(scope) {
        if (!scope.hasOwnProperty("data")) {
            scope.data = {};
        }

        var data = scope.data;

        data.basic = data.basic || <any>{};
        data.basic.user = data.basic.user || <any>{};
        data.basic.organisation = data.basic.organisation || <any>{};
        data.introduction = data.introduction || <any>{};
        data.detail = data.detail || <any>{};
        data.detail.location = data.detail.location || <any>{};
        data.motivation = data.motivation || <any>{};
        data.finance = data.finance || <any>{};
        data.extra = data.extra || <any>{};
        data.extra.hear = data.extra.hear || <any>{};

        return data;
    }

    // NOTE: _update takes an item *version*, whereas _create
    // constructs an *item plus a new version*.
    public _update(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IScope>, mercatorProposalVersion : R) : ng.IPromise<void> {
        var data = this.initializeScope(instance.scope);

        data.basic.user.name = mercatorProposalVersion.data[SIUserInfo.nick].personal_name;
        data.basic.user.lastname = mercatorProposalVersion.data[SIUserInfo.nick].family_name;
        data.basic.user.email = mercatorProposalVersion.data[SIUserInfo.nick].email;
        data.basic.createtime = mercatorProposalVersion.data[SIMetadata.nick].creation_date;

        data.basic.organisation.name = mercatorProposalVersion.data[SIOrganizationInfo.nick].name;
        data.basic.organisation.email = mercatorProposalVersion.data[SIOrganizationInfo.nick].email;
        data.basic.organisation.address = mercatorProposalVersion.data[SIOrganizationInfo.nick].street_address;
        data.basic.organisation.postcode = mercatorProposalVersion.data[SIOrganizationInfo.nick].postcode;
        data.basic.organisation.city = mercatorProposalVersion.data[SIOrganizationInfo.nick].city;
        data.basic.organisation.country = mercatorProposalVersion.data[SIOrganizationInfo.nick].country;
        data.basic.organisation.status = mercatorProposalVersion.data[SIOrganizationInfo.nick].status;
        data.basic.organisation.statustext = mercatorProposalVersion.data[SIOrganizationInfo.nick].status_other;
        data.basic.organisation.description = mercatorProposalVersion.data[SIOrganizationInfo.nick].description;
        data.basic.organisation.size = mercatorProposalVersion.data[SIOrganizationInfo.nick].size;
        data.basic.organisation.cooperationText = mercatorProposalVersion.data[SIOrganizationInfo.nick].cooperation_explanation;

        data.introduction.title = mercatorProposalVersion.data[SIIntroduction.nick].title;
        data.introduction.teaser = mercatorProposalVersion.data[SIIntroduction.nick].teaser;

        data.detail.description = mercatorProposalVersion.data[SIDetails.nick].description;
        data.detail.location.city = mercatorProposalVersion.data[SIDetails.nick].location_is_city;
        data.detail.location.country = mercatorProposalVersion.data[SIDetails.nick].location_is_country;
        data.detail.location.town = mercatorProposalVersion.data[SIDetails.nick].location_is_town;
        data.detail.location.online = mercatorProposalVersion.data[SIDetails.nick].location_is_online;
        data.detail.location.ruhr = mercatorProposalVersion.data[SIDetails.nick].location_is_linked_to_ruhr;
        data.detail.story = mercatorProposalVersion.data[SIDetails.nick].story;

        data.motivation.outcome = mercatorProposalVersion.data[SIMotivation.nick].outcome;
        data.motivation.steps = mercatorProposalVersion.data[SIMotivation.nick].steps;
        data.motivation.value = mercatorProposalVersion.data[SIMotivation.nick].value;
        data.motivation.partners = mercatorProposalVersion.data[SIMotivation.nick].partners;

        data.finance.budget = mercatorProposalVersion.data[SIFinance.nick].budget;
        data.finance.funding = mercatorProposalVersion.data[SIFinance.nick].requested_funding;
        data.finance.granted = mercatorProposalVersion.data[SIFinance.nick].granted;

        data.extra.experience = mercatorProposalVersion.data[SIExtras.nick].experience;
        data.extra.hear.colleague = mercatorProposalVersion.data[SIExtras.nick].heard_from_colleague;
        data.extra.hear.website = mercatorProposalVersion.data[SIExtras.nick].heard_from_website;
        data.extra.hear.newsletter = mercatorProposalVersion.data[SIExtras.nick].heard_from_newsletter;
        data.extra.hear.facebook = mercatorProposalVersion.data[SIExtras.nick].heard_from_facebook;
        data.extra.hear.otherDescription = mercatorProposalVersion.data[SIExtras.nick].heard_elsewhere;

        return this.$q.when();
    }

    // NOTE: see _update.
    public _create(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IScope>) : ng.IPromise<R[]> {
        var data = this.initializeScope(instance.scope);

        var mercatorProposal = new RIMercatorProposal({preliminaryNames : this.adhPreliminaryNames});
        mercatorProposal.parent = instance.scope.poolPath;
        mercatorProposal.data[SIName.nick] = new SIName.Sheet({
            name: data.introduction.title
        });

        var mercatorProposalVersion = new RIMercatorProposalVersion({preliminaryNames : this.adhPreliminaryNames});
        mercatorProposalVersion.data[SIUserInfo.nick] = new SIUserInfo.Sheet({
            personal_name: data.basic.user.name,
            family_name: data.basic.user.lastname,
            email: data.basic.user.email
        });
        mercatorProposalVersion.data[SIOrganizationInfo.nick] = new SIOrganizationInfo.Sheet({
            name: data.basic.organisation.name,
            email: data.basic.organisation.email,
            street_address: data.basic.organisation.address,
            postcode: data.basic.organisation.postcode,
            city: data.basic.organisation.city,
            country: data.basic.organisation.country,
            status: data.basic.organisation.status,
            status_other: data.basic.organisation.statustext,
            description: data.basic.organisation.description,
            size: data.basic.organisation.size,
            cooperation_explanation: data.basic.organisation.cooperationText
        });
        mercatorProposalVersion.data[SIIntroduction.nick] = new SIIntroduction.Sheet({
            title: data.introduction.title,
            teaser: data.introduction.teaser
        });
        mercatorProposalVersion.data[SIDetails.nick] = new SIDetails.Sheet({
            description: data.detail.description,
            location_is_city: data.detail.location.city,
            location_is_country: data.detail.location.country,
            location_is_town: data.detail.location.town,
            location_is_online: data.detail.location.online,
            location_is_linked_to_ruhr: data.detail.location.ruhr,
            story: data.detail.story
        });
        mercatorProposalVersion.data[SIMotivation.nick] = new SIMotivation.Sheet({
            outcome: data.motivation.outcome,
            steps: data.motivation.steps,
            value: data.motivation.value,
            partners: data.motivation.partners
        });
        mercatorProposalVersion.data[SIFinance.nick] = new SIFinance.Sheet({
            budget: data.finance.budget,
            requested_funding: data.finance.funding,
            granted: data.finance.granted
        });
        mercatorProposalVersion.data[SIExtras.nick] = new SIExtras.Sheet({
            experience: data.extra.experience,
            heard_from_colleague: data.extra.hear.colleague,
            heard_from_website: data.extra.hear.website,
            heard_from_newsletter: data.extra.hear.newsletter,
            heard_from_facebook: data.extra.hear.facebook,
            heard_elsewhere: data.extra.hear.otherDescription
        });
        mercatorProposalVersion.data[SIVersionable.nick] = new SIVersionable.Sheet({
            follows: [mercatorProposal.first_version_path]
        });
        mercatorProposalVersion.parent = mercatorProposal.path;

        console.log(mercatorProposalVersion);
        return this.$q.when([mercatorProposal, mercatorProposalVersion]);
    }

    public _edit(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IScope>, old : R) : ng.IPromise<R[]> {
        return this.$q.when([]);
    }
}


export class CreateWidget<R extends ResourcesBase.Resource> extends Widget<R> {
    constructor(
        adhConfig : AdhConfig.IService,
        adhHttp : AdhHttp.Service<any>,
        adhPreliminaryNames : AdhPreliminaryNames.Service,
        $q : ng.IQService
    ) {
        super(adhConfig, adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/Create.html";
    }
}


export class DetailWidget<R extends ResourcesBase.Resource> extends Widget<R> {
    constructor(
        adhConfig : AdhConfig.IService,
        adhHttp : AdhHttp.Service<any>,
        adhPreliminaryNames : AdhPreliminaryNames.Service,
        $q : ng.IQService
    ) {
        super(adhConfig, adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/Detail.html";
    }
}


export var listing = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            path: "@"
        }
    };
};


export var lastVersion = (
    $compile : ng.ICompileService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        scope: {
            itemPath: "@"
        },
        transclude: true,
        template: "<adh-inject></adh-inject>",
        link: (scope) => {
            adhHttp.getNewestVersionPathNoFork(scope.itemPath).then(
                (versionPath) => {
                    scope.versionPath = versionPath;
                });
        }
    };
};


export var moduleName = "adhMercatorProposal";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttp.moduleName,
            AdhInject.moduleName,
            AdhPreliminaryNames.moduleName,
            AdhResourceArea.moduleName,
            AdhResourceWidgets.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhResourceAreaProvider", "adhTopLevelStateProvider", (
            adhResourceAreaProvider : AdhResourceArea.Provider,
            adhTopLevelStateProvider : AdhTopLevelState.Provider
        ) => {
            adhTopLevelStateProvider
                .when("mercator", ["adhConfig", "$rootScope", (adhConfig, $scope) : AdhTopLevelState.IAreaInput => {
                    $scope.path = adhConfig.rest_url + adhConfig.rest_platform_path;
                    return {
                        template: "<adh-resource-wrapper>" +
                            "<adh-mercator-proposal-create data-path=\"@preliminary\" data-mode=\"edit\" data-pool-path=\"{{path}}\">" +
                            "</adh-mercator-proposal-create></adh-resource-wrapper>"
                    };
                }])
                .when("mercator-listing", ["adhConfig", "$rootScope", (adhConfig, $scope) : AdhTopLevelState.IAreaInput => {
                    $scope.path = adhConfig.rest_url + adhConfig.rest_platform_path;
                    return {
                        template: "<adh-mercator-proposal-listing data-path=\"{{path}}\">" +
                            "</adh-mercator-proposal-listing>"
                    };
                }])
                .when("mercator-detail", ["adhConfig", "$rootScope", (adhConfig, $rootScope) : AdhTopLevelState.IAreaInput => {
                    // FIXME: this always shows proposal with title "title".  for testing only.
                    $rootScope.path = adhConfig.rest_url + adhConfig.rest_platform_path + "title/";
                    return {
                        template:
                            "<adh-resource-wrapper>" +
                            "<adh-last-version data-item-path=\"{{path}}\">" +
                            "<adh-mercator-proposal-detail-view data-ng-if=\"versionPath\" data-path=\"{{versionPath}}\">" +
                            "</adh-mercator-proposal-detail-view>" +
                            "</adh-last-version>" +
                            "</adh-resource-wrapper>"
                    };
                }]);
            adhResourceAreaProvider
                .when(RIMercatorProposal.content_type, {
                     space: "content",
                     movingColumns: "is-show-show-hide"
                });
        }])
        .directive("adhMercatorProposal", ["adhConfig", "adhHttp", "adhPreliminaryNames", "$q",
            (adhConfig, adhHttp, adhPreliminaryNames, $q) => {
                var widget = new Widget(adhConfig, adhHttp, adhPreliminaryNames, $q);
                return widget.createDirective();
            }])
        .directive("adhMercatorProposalDetailView", ["adhConfig", "adhHttp", "adhPreliminaryNames", "$q",
            (adhConfig, adhHttp, adhPreliminaryNames, $q) => {
                var widget = new DetailWidget(adhConfig, adhHttp, adhPreliminaryNames, $q);
                return widget.createDirective();
            }])
        .directive("adhMercatorProposalCreate", ["adhConfig", "adhHttp", "adhPreliminaryNames", "$q",
            (adhConfig, adhHttp, adhPreliminaryNames, $q) => {
                var widget = new CreateWidget(adhConfig, adhHttp, adhPreliminaryNames, $q);
                return widget.createDirective();
            }])
        .directive("adhMercatorProposalListing", ["adhConfig", listing])
        .directive("adhLastVersion", ["$compile", "adhHttp", lastVersion]);
};
