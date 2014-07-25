import Types = require("../Types");
import AdhHttp = require("../Http/Http");
import AdhConfig = require("../Config/Config");

import Resources = require("../../Resources");


/**
 * contents of the resource with view mode.
 */
interface DetailScope<Data> extends ng.IScope {
    viewmode : string;
    content : Types.Content<Data>;
}

interface DetailRefScope<Data> extends DetailScope<Data> {
    ref : string;
}

interface IProposalVersionDetailScope<Data> extends DetailScope<Data> {
    list : () => void;
    display : () => void;
    edit : () => void;
    reset : () => void;
    commit : () => void;
}


export class ProposalVersionDetail {
    public static templateUrl: string = "/Resources/IProposalVersion/Detail.html";

    public createDirective(adhConfig: AdhConfig.Type) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/" + _class.templateUrl,
            scope: {
                content: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Types.Content<any>>,
                $scope : IProposalVersionDetailScope<any>
            ) : void => {
                $scope.list = () => {
                    $scope.viewmode = "list";
                };

                $scope.display = () => {
                    $scope.viewmode = "display";
                };

                $scope.edit = () => {
                    $scope.viewmode = "edit";
                };

                $scope.reset = () => {
                    adhHttp.get($scope.content.path).then((content) => {
                        $scope.content = content;
                    });
                    $scope.viewmode = "display";
                };

                $scope.commit = () => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);

                    $scope.$broadcast("commit");
                    $scope.viewmode = "display";
                };
            }]
        };
    }
}

export class ProposalVersionEdit {

    public createDirective(adhConfig: AdhConfig.Type) {

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Resources/IProposalVersion/Edit.html",
            scope: {
                content: "="
            }
        };
    }
}

export class ProposalVersionNew {

    public createDirective(adhHttp: ng.IHttpService, adhConfig: AdhConfig.Type, adhResources: Resources.Service) {

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Resources/IProposalVersion/New.html",
            scope: {
                onNewProposal: "="
            },
            controller: ["$scope", ($scope) => {
                $scope.proposalVersion = (new Resources.Resource("adhocracy_sample.resources.proposal.IProposalVersion"))
                    .addIDocument("", "", []);

                $scope.paragraphVersions = [];

                $scope.addParagraphVersion = () => {
                    $scope.paragraphVersions.push(new Resources.Resource("adhocracy_sample.resources.paragraph.IParagraphVersion")
                                                  .addIParagraph(""));
                };

                $scope.commit = () => {
                    adhResources.postProposalWithParagraphs($scope.proposalVersion, $scope.paragraphVersions).then((resp) => {
                        adhHttp.get(resp.path).then((respGet) => {
                            $scope.onNewProposal(respGet);
                        });
                    });
                };
            }]
        };
    }
}

export class SectionVersionDetail {

    public createDirective(adhConfig: AdhConfig.Type, recursionHelper) {

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Resources/ISectionVersion/Detail.html",
            compile: (element) => recursionHelper.compile(element),
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Types.Content<Resources.HasISectionSheet>>,
                $scope : DetailRefScope<Resources.HasISectionSheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then((content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class ParagraphVersionDetail {

    public createDirective(adhConfig: AdhConfig.Type) {

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Resources/IParagraphVersion/Detail.html",
            scope: {
                ref: "=",
                viewmode: "="
            },
            controller: ["adhHttp", "$scope", (
                adhHttp : AdhHttp.Service<Types.Content<Resources.HasIParagraphSheet>>,
                $scope : DetailRefScope<Resources.HasIParagraphSheet>
            ) : void => {
                var commit = (event, ...args) => {
                    adhHttp.postNewVersion($scope.content.path, $scope.content);
                };

                // keep pristine copy in sync with cache.  FIXME: this should be done in one gulp with postNewVersion
                adhHttp.get($scope.ref).then((content) => {
                    $scope.content = content;
                });

                // save working copy on 'commit' event from containing document.
                $scope.$on("commit", commit);
            }]
        };
    }
}

export class DocumentSheetEdit {

    public createDirective(adhHttp, $q, adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Sheets/IDocument/Edit.html",
            scope: {
                sheet: "="
            },
            controller: ["$scope", ($scope) => {
                var versionPromises = $scope.sheet.elements.map((path) =>
                    adhHttp.get(decodeURIComponent(path))
                        .then((resp) => resp.data)
                );

                $q.all(versionPromises).then((versions) =>
                    $scope.sectionVersions = versions
                );
            }]
        };
    }
}

export class DocumentSheetShow {

    public createDirective (adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Sheets/IDocument/Show.html",
            scope: {
                sheet: "="
            }
        };
    }
}

export class ParagraphSheetEdit {
    public createDirective (adhConfig: AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/Sheets/IParagraph/Edit.html",
            scope: {
                sheet: "="
            }
        };
    }
}
