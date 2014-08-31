import AdhResource = require("../../Resources");
import RIComment = require("../../Resources_/adhocracy_sample/resources/comment/IComment");

import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhListing = require("../Listing/Listing");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");

import Util = require("../Util/Util");

var pkgLocation = "/Comment";


export interface ICommentAdapter<T extends AdhResource.Content<any>> extends AdhListing.IListingContainerAdapter {
    create(settings : any) : T;
    createItem(settings : any) : any;
    derive(oldVersion : T, settings : any) : T;
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
                    var resource = _self.adapter.create({preliminaryNames: adhPreliminaryNames});
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


export interface ICommentResourceScope extends AdhResourceWidgets.IResourceWidgetScope {
    refersTo : string;
    poolPath : string;
    show : {
        createForm : boolean;
    };
    createComment() : void;
    cancelCreateComment() : void;
    afterCreateComment() : ng.IPromise<void>;
}

export class CommentResource extends AdhResourceWidgets.ResourceWidget<any, ICommentResourceScope> {
    constructor(
        private adapter : ICommentAdapter<any>,
        adhConfig : AdhConfig.Type,
        adhHttp,
        adhPreliminaryNames : AdhPreliminaryNames,
        $q : ng.IQService
    ) {
        super(adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/CommentDetail.html";
    }

    createRecursionDirective(recursionHelper) {
        var self = this;

        var directive = this.createDirective();
        directive.compile = (element) => recursionHelper.compile(element, directive.link);

        directive.scope.refersTo = "@";
        directive.scope.poolPath = "@";

        directive.link = (scope : ICommentResourceScope, element, attrs, wrapper) => {
            var instance = self.link(scope, element, attrs, wrapper);

            scope.show = {
                createForm: false
            };

            scope.createComment = () => {
                scope.show.createForm = true;
            };

            scope.cancelCreateComment = () => {
                scope.show.createForm = false;
            };

            scope.afterCreateComment = () => {
                return this.update(instance).then(() => {
                    scope.show.createForm = false;
                });
            };
        };

        return directive;
    }

    public _handleDelete(instance, path : string) {
        return this.$q.when();
    }

    public _update(instance, resource) {
        instance.scope.data = {
            content: this.adapter.content(resource),
            creator: this.adapter.creator(resource),
            creationDate: this.adapter.creationDate(resource),
            modificationDate: this.adapter.modificationDate(resource),
            commentCount: this.adapter.commentCount(resource),
            comments: this.adapter.elemRefs(resource),
            replyPoolPath: this.adapter.poolPath(resource)
        };
        return this.$q.when();
    }

    public _provide(instance) {
        var self = this;

        var updateFromScope = (resource) => {
            self.adapter.content(resource, instance.scope.data.content);
            self.adapter.refersTo(resource, instance.scope.refersTo);
        };

        if (self.adhPreliminaryNames.isPreliminary(instance.scope.path)) {
            var item = self.adapter.createItem({
                preliminaryNames: self.adhPreliminaryNames,
                name: "comment"
            });
            item.parent = instance.scope.poolPath;

            var version = self.adapter.create({
                preliminaryNames: self.adhPreliminaryNames,
                follows: item.first_version_path
            });
            updateFromScope(version);
            version.parent = item.path;

            return self.$q.when([item, version]);
        } else {
            return self.adhHttp.get(instance.scope.path).then((oldVersion) => {
                var resource = self.adapter.derive(oldVersion, {preliminaryNames: self.adhPreliminaryNames});
                updateFromScope(resource);
                resource.parent = Util.parentPath(oldVersion.path);
                return [resource];
            });
        }
    }
}

export var commentDetail = () => {
    return {
        restrict: "E",
        scope: {
            path: "="
        },
        template: "<adh-resource-wrapper><adh-comment-resource data-path=\"{{path}}\" data-mode=\"display\">" +
            "</adh-comment-resource></adh-resource-wrapper>"
    };
};
