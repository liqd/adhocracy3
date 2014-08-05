import AdhConfig = require("../Config/Config");
import AdhResource = require("../../Resources");

import Util = require("../Util/Util");

var pkgLocation = "/Comment";

export interface ICommentAdapter<T extends AdhResource.Content<any>> {
    create() : T;
    content(res : T) : string;
    content(res : T, value : string) : T;
    refersTo(res : T) : string;
    refersTo(res : T, value : string) : T;
    creator(red : T) : string;
}

export class CommentCreate {
    constructor(private adapter : ICommentAdapter<any>) {}

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self : CommentCreate = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentCreate.html",
            scope: {
                refersTo: "@"  // path of a commentable version
            },
            controller: ["$scope", "adhHttp", ($scope, adhHttp) => {
                $scope.errors = [];

                var displayErrors = (errors) => {
                    $scope.errors = errors;
                    throw errors;
                };

                $scope.create = () => {
                    var res = _self.adapter.create();
                    _self.adapter.content(res, $scope.content);
                    _self.adapter.refersTo(res, $scope.refersTo);

                    var comment = {
                        content_type: "adhocracy_sample.resources.comment.IComment",
                        data: {
                            "adhocracy.sheets.name.IName": {
                                name: "comment"
                            }
                        }
                    };

                    // NOTE: If poolPath is defined like this, answers to comments are placed
                    // inside other comment. This should be changed if we prefer to flatten
                    // the hierarchy.
                    var poolPath = Util.parentPath($scope.refersTo);
                    return adhHttp.postToPool(poolPath, comment)
                        .then(adhHttp.resolve.bind(adhHttp), displayErrors)
                        .then((comment) => adhHttp.postNewVersion(comment.first_version_path, res))
                        .then((x) => x, displayErrors);
                };
            }]
        };
    }
}

export class CommentDetail {
    constructor(private adapter : ICommentAdapter<any>) {}

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self : CommentDetail = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentDetail.html",
            scope: {
                path: "=",  // path to a comment that should be displayed
                viemode: "=" // "list" or "edit"
            },
            controller: ["$scope", "adhHttp", "adhDone", ($scope, adhHttp, adhDone) => {
                var res;

                $scope.edit = () => {
                    _self.adapter.content(res, $scope.content);
                    // FIXME: send res via adhHttp
                };

                adhHttp.getNewestVersionPath($scope.path)
                    .then((path) => adhHttp.resolve(path))
                    .then((_res) => {
                        res = <AdhResource.Content<any>>_res;
                        $scope.content = _self.adapter.content(res);
                        $scope.creator = _self.adapter.creator(res);
                    })
                    .then(adhDone);
            }]
        };
    }
}
