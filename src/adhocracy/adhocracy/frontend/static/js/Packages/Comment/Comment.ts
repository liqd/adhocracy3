import AdhResource = require("../../Resources");
import SICommentable = require("../../Resources_/adhocracy_sample/sheets/comment/ICommentable");

import AdhConfig = require("../Config/Config");
import AdhListing = require("../Listing/Listing");
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

export class ListingCommentableAdapter implements AdhListing.IListingContainerAdapter {
    public elemRefs(container : AdhResource.Content<SICommentable.HasAdhocracySampleSheetsCommentICommentable>) {
        return container.data["adhocracy_sample.sheets.comment.ICommentable"].comments;
    }
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
                var versionPromise = adhHttp.resolve($scope.path);

                var displayErrors = (errors) => {
                    $scope.errors = errors;
                    throw errors;
                };

                var updateScope = () => {
                    return versionPromise.then((_res) => {
                        res = <AdhResource.Content<any>>_res;
                        $scope.data = {
                            content: _self.adapter.content(res),
                            creator: _self.adapter.creator(res)
                        };
                    });
                };

                $scope.errors = [];

                $scope.edit = () => {
                    $scope.viewmode = "edit";
                };

                $scope.cancel = () => {
                    $scope.viewmode = "list";
                    $scope.errors = [];
                };

                $scope.save = () => {
                    _self.adapter.content(res, $scope.data.content);
                    return versionPromise.then((version) => {
                        versionPromise = adhHttp.postNewVersion(version.path, res)
                            .then((_res) => adhHttp.resolve(_res.path), displayErrors);
                        return updateScope().then(() => {
                            $scope.viewmode = "list";
                        });
                    });
                };

                updateScope().then(adhDone);
            }]
        };
    }
}
