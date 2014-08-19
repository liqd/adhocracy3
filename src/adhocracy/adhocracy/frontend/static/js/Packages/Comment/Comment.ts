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
        // The backend sends all versions that refere to container. So we need
        // to find out which ones are most recent ourselves.

        var refs : string[] = container.data["adhocracy_sample.sheets.comment.ICommentable"].comments;
        var latestVersions : string[] = [];
        var lastCommentPath : string = undefined;

        refs.sort().reverse().forEach((versionPath : string) => {
            var commentPath = Util.parentPath(versionPath);
            if (commentPath !== lastCommentPath) {
                latestVersions.push(versionPath);
                lastCommentPath = commentPath;
            }
        });

        return latestVersions;
    }

    public poolPath(container : AdhResource.Content<SICommentable.HasAdhocracySampleSheetsCommentICommentable>) {
        // NOTE: If poolPath is defined like this, answers to comments are placed
        // inside other comment. This should be changed if we prefer to flatten
        // the hierarchy.
        return Util.parentPath(container.path);
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
                refersTo: "@",  // path of a commentable version
                poolPath: "@",  // pool where new comments should be posted to
                onNew: "="  // callback to call after successful creation
            },
            controller: ["$scope", "adhHttp", ($scope, adhHttp) => {
                $scope.errors = [];

                var displayErrors = (errors) => {
                    $scope.errors = errors;
                    throw errors;
                };

                var onNew = () => {
                    if (typeof $scope.onNew !== "undefined") {
                        $scope.onNew();
                    }
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

                    return adhHttp.postToPool($scope.poolPath, comment)
                        .then(adhHttp.resolve.bind(adhHttp), displayErrors)
                        .then((comment) => adhHttp.postNewVersion(comment.first_version_path, res))
                        .then(onNew, displayErrors);
                };
            }]
        };
    }
}

export class CommentDetail {
    constructor(private adapter : ICommentAdapter<any>) {}

    public createDirective(adhConfig : AdhConfig.Type, recursionHelper) {
        var _self : CommentDetail = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentDetail.html",
            scope: {
                path: "=",  // path to a comment that should be displayed
                viemode: "=" // "list" or "edit"
            },
            compile: (element) => recursionHelper.compile(element),
            controller: ["$scope", "adhHttp", "adhDone", ($scope, adhHttp, adhDone) => {
                var res : AdhResource.Content<any>;
                var versionPromise = adhHttp.resolve($scope.path);

                var displayErrors = (errors) => {
                    $scope.errors = errors;
                    throw errors;
                };

                var updateScope = () => {
                    return versionPromise.then((_res : AdhResource.Content<any>) => {
                        res = _res;
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
