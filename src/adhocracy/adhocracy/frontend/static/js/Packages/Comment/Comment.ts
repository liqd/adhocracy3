import AdhResource = require("../../Resources");
import RIComment = require("../../Resources_/adhocracy_sample/resources/comment/IComment");

import AdhConfig = require("../Config/Config");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhListing = require("../Listing/Listing");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");

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


export class CommentResource extends AdhResourceWidgets.ResourceWidget<any, any> {
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
        var directive = this.createDirective();
        directive.compile = (element) => recursionHelper.compile(element, directive.link);
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
            poolPath: this.adapter.poolPath(resource)
        };
        return this.$q.when();
    }

    public _provide(instance) {
        var resources = [];

        // FIXME use derive
        var resource = this.adapter.create(this.adhPreliminaryNames);
        this.adapter.content(resource, instance.scope.content);
        this.adapter.refersTo(resource, instance.scope.refersTo);
        resources.push(resource);

        if (this.adhPreliminaryNames.isPreliminary(instance.scope.path)) {
            var comment = new RIComment({
                preliminaryNames: this.adhPreliminaryNames,
                name: "comment"
            });
            resources.push(comment);
        }

        return this.$q.when(resources);
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
