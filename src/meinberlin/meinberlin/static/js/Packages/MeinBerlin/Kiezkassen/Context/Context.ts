import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhHttp = require("../../../Http/Http");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUser = require("../../../User/User");

import AdhMeinBerlinWorkbench = require("../Workbench/Workbench");

import RIComment = require("../../../../Resources_/adhocracy_core/resources/comment/IComment");
import RICommentVersion = require("../../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");
import RIProposal = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposal");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIComment = require("../../../../Resources_/adhocracy_core/sheets/comment/IComment");

var pkgLocation = "/MeinBerlin/Kiezkassen/Context";


export var headerDirective = (adhConfig : AdhConfig.IService, adhTopLevelState : AdhTopLevelState.Service) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/header.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };

};


export var moduleName = "adhMeinBerlinKiezkassenContext";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhHttp.moduleName,
            AdhMeinBerlinWorkbench.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName,
            AdhUser.moduleName
        ])
        .directive("adhKiezkassenContextHeader", ["adhConfig", "adhTopLevelState", headerDirective])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerContext("kiezkassen");
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                .template("kiezkassen", ["adhConfig", "$templateRequest", (
                    adhConfig : AdhConfig.IService,
                    $templateRequest : angular.ITemplateRequestService
                ) => {
                    return $templateRequest(adhConfig.pkg_path + pkgLocation + "/template.html");
                }])
                .default(RIKiezkassenProcess, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .default(RIKiezkassenProcess, "create_proposal", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIKiezkassenProcess, "create_proposal", RIKiezkassenProcess.content_type, "kiezkassen", [
                    "adhHttp", "adhUser", (
                        adhHttp : AdhHttp.Service<any>,
                        adhUser : AdhUser.Service
                    ) => (resource : RIKiezkassenProcess) => {
                        return adhUser.ready.then(() => {
                            return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                                if (!options.POST) {
                                    throw 401;
                                } else {
                                    return {};
                                }
                            });
                        });
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "edit", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "edit", RIKiezkassenProcess.content_type, "kiezkassen", [
                    "adhHttp", "adhUser", (
                        adhHttp : AdhHttp.Service<any>,
                        adhUser : AdhUser.Service
                    ) => (item : RIProposal, version : RIProposalVersion) => {
                        return adhUser.ready.then(() => {
                            return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                                if (!options.POST) {
                                    throw 401;
                                } else {
                                    return {
                                        proposalUrl: version.path
                                    };
                                }
                            });
                        });
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "", RIKiezkassenProcess.content_type, "kiezkassen", [
                    () => (item : RIProposal, version : RIProposalVersion) => {
                        return {
                            proposalUrl: version.path
                        };
                    }])
                .defaultVersionable(RIProposal, RIProposalVersion, "comments", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIProposal, RIProposalVersion, "comments", RIKiezkassenProcess.content_type, "kiezkassen", [
                    () => (item : RIProposal, version : RIProposalVersion) => {
                        return {
                            commentableUrl: version.path,
                            proposalUrl: version.path
                        };
                    }])
                .defaultVersionable(RIComment, RICommentVersion, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specificVersionable(RIComment, RICommentVersion, "", RIKiezkassenProcess.content_type, "kiezkassen", ["adhHttp", "$q", (
                    adhHttp : AdhHttp.Service<any>,
                    $q : angular.IQService
                ) => {
                    var getCommentableUrl = (resource) : angular.IPromise<any> => {
                        if (resource.content_type !== RICommentVersion.content_type) {
                            return $q.when(resource);
                        } else {
                            var url = resource.data[SIComment.nick].refers_to;
                            return adhHttp.get(url).then(getCommentableUrl);
                        }
                    };

                    return (item : RIComment, version : RICommentVersion) => {
                        return getCommentableUrl(version).then((commentable) => {
                            return {
                                commentableUrl: commentable.path,
                                proposalUrl: commentable.path
                            };
                        });
                    };
                }]);
        }]);
};
