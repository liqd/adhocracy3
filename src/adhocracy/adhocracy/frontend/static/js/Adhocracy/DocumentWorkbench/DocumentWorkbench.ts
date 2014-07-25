/// <reference path="../../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import Types = require("../Types");
import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhUser = require("../User/User");
import Resources = require("../../Resources");

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

export class DocumentWorkbench {
    public static templateUrl: string = "/Pages/DocumentWorkbench.html";

    public createDirective(adhConfig: AdhConfig.Type, adhResources: Resources.Service) {
        var _self = this;
        var _class = (<any>_self).constructor;

        return {
            restrict: "E",
            templateUrl: adhConfig.template_path + "/" + _class.templateUrl,
            controller: ["adhHttp", "$scope", "adhUser", (
                adhHttp : AdhHttp.Service<Types.Content<Resources.HasIDocumentSheet>>,
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
    }
}
