/// <reference path="../../../../../lib2/types/lodash.d.ts"/>
/// <reference path="../../../../../lib2/types/moment.d.ts"/>

import * as AdhBadge from "../../../Core/Badge/Badge";
import * as AdhConfig from "../../../Core/Config/Config";
import * as AdhEmbed from "../../../Core/Embed/Embed";
import * as AdhHttp from "../../../Core/Http/Http";
import * as AdhPermissions from "../../../Core/Permissions/Permissions";
import * as AdhResourceArea from "../../../Core/ResourceArea/ResourceArea";
import * as AdhTopLevelState from "../../../Core/TopLevelState/TopLevelState";

import * as ResourcesBase from "../../../../ResourcesBase";

import RIPoll from "../../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IPoll";
import RIProposalVersion from "../../../../Resources_/adhocracy_core/resources/proposal/IProposalVersion";
import RIStadtforumProcess from "../../../../Resources_/adhocracy_meinberlin/resources/stadtforum/IProcess";

import * as SIDescription from "../../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SITitle from "../../../../Resources_/adhocracy_core/sheets/title/ITitle";
import * as SIWorkflow from "../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";

var pkgLocation = "/Meinberlin/Stadtforum/Process";


export var workbenchDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        scope: {
            processProperties: "="
        },
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("contentType", scope));
            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    adhHttp.get(processUrl).then((resource) => {
                        scope.currentPhase = resource.data[SIWorkflow.nick].workflow_state;
                    });
                }
            });
        }

    };
};

export var proposalDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalDetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
        }
    };
};

export var proposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalCreateColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };
};

export var proposalEditColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalEditColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
        }
    };
};

export var detailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };
};

export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhEmbed: AdhEmbed.Service,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    $q : angular.IQService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            AdhBadge.getBadgeFacets(adhHttp, $q)(scope.path).then((facets) => {
                scope.facets = facets;
            });

            scope.data = {};

            scope.sorts = [{
                key: "rates",
                name: "TR__RATES",
                index: "rates",
                reverse: true
            }, {
                key: "item_creation_date",
                name: "TR__CREATION_DATE",
                index: "item_creation_date",
                reverse: true
            }];
            scope.sort = "item_creation_date";

            scope.contentType = RIProposalVersion.content_type;

            scope.$watch("path", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        scope.data.title = resource.data[SITitle.nick].title;
                        scope.data.shortDescription = resource.data[SIDescription.nick].short_description;
                    });
                }
            });
            adhPermissions.bindScope(scope, () => scope.path);

            var context = adhEmbed.getContext();
            scope.hasResourceHeader = (context === "mein.bärlin.de");
        }
    };
};

export var registerRoutes = (
    processType : string = "",
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider
        .default(RIStadtforumProcess, "", processType, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .default(RIStadtforumProcess, "create_proposal", processType, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specific(RIStadtforumProcess, "create_proposal", processType, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (resource : ResourcesBase.IResource) => {
                return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                    if (!options.canPost(RIPoll.content_type)) {
                        throw 401;
                    } else {
                        return {};
                    }
                });
            }])
        .defaultVersionable(RIPoll, RIProposalVersion, "", processType, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIPoll, RIProposalVersion, "", processType, context, [
            () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return {
                    proposalUrl: version.path
                };
            }])
        .defaultVersionable(RIPoll, RIProposalVersion, "edit", processType, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIPoll, RIProposalVersion, "edit", processType, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {
                            proposalUrl: version.path
                        };
                    }
                });
            }])
        .defaultVersionable(RIPoll, RIProposalVersion, "comments", processType, context, {
            space: "content",
            movingColumns: "is-collapse-show-show"
        })
        .specificVersionable(RIPoll, RIProposalVersion, "comments", processType, context, [
            () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return {
                    commentableUrl: version.path,
                    commentCloseUrl: version.path,
                    proposalUrl: version.path
                };
            }]);
};
