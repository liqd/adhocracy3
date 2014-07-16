import Types = require("./Types");
import AdhHttp = require("./Services/Http");
import AdhUser = require("./Services/User");
import AdhConfig = require("./Services/Config");
import AdhCrossWindowMessaging = require("./Services/CrossWindowMessaging");

import Resources = require("./Resources");


/**
 * contents of the resource with view mode.
 */
interface IDocument<Data> {
    viewmode : string;
    content : Types.Content<Data>;
}

interface IDocumentWorkbenchScope<Data> extends ng.IScope {
    pool : Types.Content<Data>;
    poolEntries : IDocument<Data>[];
    doc : IDocument<Data>;  // (iterates over document list with ng-repeat)
    insertParagraph : any;
    user : AdhUser.User;
}

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


export var adhDocumentWorkbench = (
        adhConfig: AdhConfig.Type,
        adhResources: Resources.Service,
        adhCrossWindowMessaging: AdhCrossWindowMessaging.Service
    ) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Pages/DocumentWorkbench.html",
        controller: ["adhHttp", "$scope", "adhUser", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasIDocumentSheet>>,
            $scope : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>,
            user : AdhUser.User
        ) : void => {
            $scope.insertParagraph = (proposalVersion: Types.Content<Resources.HasIDocumentSheet>) => {
                $scope.poolEntries.push({viewmode: "list", content: proposalVersion});
            };

            adhHttp.get(adhConfig.root_path).then((pool) => {
                $scope.pool = pool;
                $scope.poolEntries = [];
                $scope.user = user;

                // FIXME: factor out getting the head version of a DAG.

                var fetchDocumentHead = (n : number, dag : Types.Content<Resources.HasIDocumentSheet>) : ng.IPromise<void> => {
                    return adhResources.getNewestVersionPath(dag.path)
                        .then((headPath) => adhHttp.get(headPath))
                        .then((headContent) => {
                            if (n in $scope.poolEntries) {
                                // leave original headContentRef intact,
                                // just replace subscription handle and
                                // content object.
                                $scope.poolEntries[n].content = headContent;
                            } else {
                                // bind original headContentRef to model.
                                $scope.poolEntries[n] = {viewmode: "list", content: headContent};
                            }
                        });
                };

                var dagRefs : string[] = pool.data["adhocracy.sheets.pool.IPool"].elements;
                for (var i = 0; i < dagRefs.length; i++) {
                    ((dagRefIx : number) => {
                        var dagRefPath : string = dagRefs[dagRefIx];
                        adhHttp.get(dagRefPath).then((dag) => fetchDocumentHead(dagRefIx, dag));
                    })(i);
                }
            });
        }]
    };
};

export var adhProposalVersionDetail = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Resources/IProposalVersion/Detail.html",
        scope: {
            content: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<any>>,
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
};

export var adhProposalVersionEdit = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Resources/IProposalVersion/Edit.html",
        scope: {
            content: "="
        }
    };
};

export var adhProposalVersionNew = (
    adhHttp: ng.IHttpService,
    adhConfig: AdhConfig.Type,
    adhResources: Resources.Service
) => {
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
};

export var adhSectionVersionDetail = (adhConfig: AdhConfig.Type, recursionHelper) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Resources/ISectionVersion/Detail.html",
        compile: (element) => recursionHelper.compile(element),
        scope: {
            ref: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasISectionSheet>>,
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
};

export var adhParagraphVersionDetail = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Resources/IParagraphVersion/Detail.html",
        scope: {
            ref: "=",
            viewmode: "="
        },
        controller: ["adhHttp", "$scope", (
            adhHttp : AdhHttp.IService<Types.Content<Resources.HasIParagraphSheet>>,
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
};

export var adhDocumentSheetEdit = (adhHttp, $q, adhConfig: AdhConfig.Type) => {
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
};

export var adhDocumentSheetShow = (adhConfig: AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Sheets/IDocument/Show.html",
        scope: {
            sheet: "="
        }
    };
};

export var adhParagraphSheetEdit = (adhConfig) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.template_path + "/Sheets/IParagraph/Edit.html",
        scope: {
            sheet: "="
        }
    };
};

// FIXME: this doesn't really belong here, but to Services/User.ts.
export var adhRegister = (adhConfig) => {
    return {
        templateUrl: adhConfig.template_path + "/Register.html",
        scope: { },
        controller: ["$scope", "adhHttp", ($scope, adhHttp) => {
            $scope.postRegistration = (): void => {

                // FIXME: sanity check input some more
                // (password_repeat, do not post if email smells
                // funny, ...)

                adhHttp.post("/principals/users/", {
                    "content_type": "adhocracy.resources.principal.IUser",
                    "data": {
                        "adhocracy.sheets.user.UserBasicSchema": {
                            "name": $scope.username,
                            "email": $scope.email
                        },
                        "adhocracy.sheets.user.IPasswordAuthentication": {
                            "password": $scope.password
                        }
                    }
                }).then(() => {
                    throw "handler for registration response not implemented.";
                });
            };
        }]
    };
};
