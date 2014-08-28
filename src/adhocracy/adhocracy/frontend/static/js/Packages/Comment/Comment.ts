import AdhResource = require("../../Resources");
import RIComment = require("../../Resources_/adhocracy_sample/resources/comment/IComment");

import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhListing = require("../Listing/Listing");
import Util = require("../Util/Util");

var pkgLocation = "/Comment";


export interface ICommentAdapter<T extends AdhResource.Content<any>> extends AdhListing.IListingContainerAdapter {
    create(pn : AdhPreliminaryNames) : T;
    content(resource : T) : string;
    content(resource : T, value : string) : T;
    refersTo(resource : T) : string;
    refersTo(resource : T, value : string) : T;
    creator(resource : T) : string;
    creationDate(resource : T) : string;
    modificationDate(resource : T) : string;
    commentCount(resource : T) : number;
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
                onNew: "=",  // callback to call after successful creation
                onCancel: "="  // callback to call when cancel was clicked
            },
            controller: ["$scope", "adhHttp", "adhPreliminaryNames", ($scope, adhHttp, adhPreliminaryNames) => {
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
                    var resource = _self.adapter.create(adhPreliminaryNames);
                    _self.adapter.content(resource, $scope.content);
                    _self.adapter.refersTo(resource, $scope.refersTo);

                    var comment = new RIComment({preliminaryNames: adhPreliminaryNames, name: "comment"});

                    return adhHttp.postToPool($scope.poolPath, comment)
                        .then(adhHttp.resolve.bind(adhHttp), displayErrors)
                        .then((comment) => adhHttp.postNewVersion(comment.first_version_path, resource))
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
                var resource : AdhResource.Content<any>;

                var displayErrors = (errors) => {
                    $scope.errors = errors;
                    throw errors;
                };

                var updateScope = (path) => {
                    $scope.path = path;
                    return adhHttp.resolve(path).then((_resource : AdhResource.Content<any>) => {
                        resource = _resource;
                        $scope.data = {
                            content: _self.adapter.content(resource),
                            creator: _self.adapter.creator(resource),
                            creationDate: _self.adapter.creationDate(resource),
                            modificationDate: _self.adapter.modificationDate(resource),
                            commentCount: _self.adapter.commentCount(resource),
                            comments: _self.adapter.elemRefs(resource),
                            poolPath: _self.adapter.poolPath(resource)
                        };
                    });
                };

                $scope.errors = [];
                $scope.show = {
                    createForm: false
                };

                $scope.edit = () => {
                    $scope.viewmode = "edit";
                };

                $scope.cancel = () => {
                    $scope.viewmode = "list";
                    $scope.errors = [];
                };

                $scope.save = () => {
                    _self.adapter.content(resource, $scope.data.content);
                    return adhHttp.postNewVersion($scope.path, resource)
                        .then((_resource) => _resource.path, displayErrors)
                        .then(updateScope)
                        .then(() => {
                            $scope.viewmode = "list";
                        });
                };

                $scope.createComment = () => {
                    $scope.show.createForm = true;
                };

                $scope.cancelCreateComment = () => {
                    $scope.show.createForm = false;
                };

                $scope.afterCreateComment = () => {
                    return adhHttp.getNewestVersionPath(Util.parentPath($scope.path))
                        .then(updateScope)
                        .then(() => {
                            $scope.show.createForm = false;
                        });
                };

                updateScope($scope.path).then(adhDone);
            }]
        };
    }
}
