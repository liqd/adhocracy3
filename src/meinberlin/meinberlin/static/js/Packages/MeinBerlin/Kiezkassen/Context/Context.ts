import AdhConfig = require("../../../Config/Config");
import AdhEmbed = require("../../../Embed/Embed");
import AdhHttp = require("../../../Http/Http");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUser = require("../../../User/User");
import AdhUtil = require("../../../Util/Util");

import AdhMeinBerlinWorkbench = require("../../Workbench/Workbench");

import RICommentVersion = require("../../../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIKiezkassenProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProcess");
import RIProposalVersion = require("../../../../Resources_/adhocracy_meinberlin/resources/kiezkassen/IProposalVersion");
import SIComment = require("../../../../Resources_/adhocracy_core/sheets/comment/IComment");

var pkgLocation = "/MeinBerlin/Kiezkassen/Context";


export var headerDirective = (adhConfig : AdhConfig.IService, adhTopLevelState : AdhTopLevelState.Service) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/header.html",
        link: (scope) => {
            adhTopLevelState.bind("processUrl", scope);
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
                .default(RIKiezkassenProcess.content_type, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-hide-hide"
                })
                .default(RIKiezkassenProcess.content_type, "create_proposal", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIKiezkassenProcess.content_type, "create_proposal", RIKiezkassenProcess.content_type, "kiezkassen", [
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
                .default(RIProposalVersion.content_type, "edit", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIProposalVersion.content_type, "edit", RIKiezkassenProcess.content_type, "kiezkassen", [
                    "adhHttp", "adhUser", (
                        adhHttp : AdhHttp.Service<any>,
                        adhUser : AdhUser.Service
                    ) => (resource : RIProposalVersion) => {
                        return adhUser.ready.then(() => {
                            return adhHttp.options(AdhUtil.parentPath(resource.path)).then((options : AdhHttp.IOptions) => {
                                if (!options.POST) {
                                    throw 401;
                                } else {
                                    return {
                                        proposalUrl: resource.path
                                    };
                                }
                            });
                        });
                    }])
                .default(RIProposalVersion.content_type, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-show-show-hide"
                })
                .specific(RIProposalVersion.content_type, "", RIKiezkassenProcess.content_type, "kiezkassen", [
                    () => (resource : RIProposalVersion) => {
                        return {
                            proposalUrl: resource.path
                        };
                    }])
                .default(RIProposalVersion.content_type, "comments", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIProposalVersion.content_type, "comments", RIKiezkassenProcess.content_type, "kiezkassen", [
                    () => (resource : RIProposalVersion) => {
                        return {
                            commentableUrl: resource.path,
                            proposalUrl: resource.path
                        };
                    }])
                .default(RICommentVersion.content_type, "", RIKiezkassenProcess.content_type, "kiezkassen", {
                    space: "content",
                    movingColumns: "is-collapse-show-show"
                })
                .specific(RIProposalVersion.content_type, "", RIKiezkassenProcess.content_type, "kiezkassen", ["adhHttp", "$q", (
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

                    return (resource : RICommentVersion) => {
                        return getCommentableUrl(resource).then((commentable) => {
                            return {
                                commentableUrl: commentable.path,
                                proposalUrl: commentable.path
                            };
                        });
                    };
                }]);
        }]);
};
