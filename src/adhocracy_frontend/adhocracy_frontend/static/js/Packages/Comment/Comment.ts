import _ = require("lodash");

import AdhResourcesBase = require("../../ResourcesBase");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPermissions = require("../Permissions/Permissions");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhListing = require("../Listing/Listing");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");
import AdhUser = require("../User/User");
import RIExternalResource = require("../../Resources_/adhocracy_core/resources/external_resource/IExternalResource");
import SIPool = require("../../Resources_/adhocracy_core/sheets/pool/IPool");
import Util = require("../Util/Util");

var pkgLocation = "/Comment";


export interface ICommentAdapter<T extends AdhResourcesBase.Resource> extends AdhListing.IListingContainerAdapter {
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


export interface ICommentResourceScope extends AdhResourceWidgets.IResourceWidgetScope {
    refersTo : string;
    poolPath : string;
    poolOptions : AdhHttp.IOptions;
    createPath : string;
    show : {
        createForm : boolean;
    };
    createComment() : void;
    cancelCreateComment() : void;
    afterCreateComment() : ng.IPromise<void>;
    data : {
        content : string;
        creator : string;
        creationDate : string;
        modificationDate : string;
        commentCount : number;
        comments : string[];
        replyPoolPath : string;
    };
}

export class CommentResource<R extends AdhResourcesBase.Resource> extends AdhResourceWidgets.ResourceWidget<R, ICommentResourceScope> {
    constructor(
        private adapter : ICommentAdapter<R>,
        adhConfig : AdhConfig.Type,
        adhHttp : AdhHttp.Service<any>,
        public adhPermissions : AdhPermissions.Service,
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
                scope.createPath = self.adhPreliminaryNames.nextPreliminary();
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

    public _handleDelete(instance : AdhResourceWidgets.IResourceWidgetInstance<R, ICommentResourceScope>, path : string) {
        return this.$q.when();
    }

    public _update(
        instance : AdhResourceWidgets.IResourceWidgetInstance<R, ICommentResourceScope>,
        resource : R
    ) {
        var scope : ICommentResourceScope = instance.scope;
        scope.data = {
            content: this.adapter.content(resource),
            creator: this.adapter.creator(resource),
            creationDate: this.adapter.creationDate(resource),
            modificationDate: this.adapter.modificationDate(resource),
            commentCount: this.adapter.commentCount(resource),
            comments: this.adapter.elemRefs(resource),
            replyPoolPath: this.adapter.poolPath(resource)
        };
        this.adhPermissions.bindScope(scope, scope.data.replyPoolPath, "poolOptions");
        return this.$q.when();
    }

    public _create(instance : AdhResourceWidgets.IResourceWidgetInstance<R, ICommentResourceScope>) {
        var item = this.adapter.createItem({
            preliminaryNames: this.adhPreliminaryNames,
            name: "comment"
        });
        item.parent = instance.scope.poolPath;

        var version = this.adapter.create({
            preliminaryNames: this.adhPreliminaryNames,
            follows: [item.first_version_path]
        });
        this.adapter.content(version, instance.scope.data.content);
        this.adapter.refersTo(version, instance.scope.refersTo);
        version.parent = item.path;

        return this.$q.when([item, version]);
    }

    public _edit(instance : AdhResourceWidgets.IResourceWidgetInstance<R, ICommentResourceScope>, oldVersion : R) {
        var resource = this.adapter.derive(oldVersion, {preliminaryNames: this.adhPreliminaryNames});
        this.adapter.content(resource, instance.scope.data.content);
        resource.parent = Util.parentPath(oldVersion.path);
        return this.$q.when([resource]);
    }
}

export class CommentCreate<R extends AdhResourcesBase.Resource> extends CommentResource<R> {
    constructor(
        adapter : ICommentAdapter<R>,
        adhConfig : AdhConfig.Type,
        adhHttp : AdhHttp.Service<any>,
        public adhPermissions : AdhPermissions.Service,
        adhPreliminaryNames : AdhPreliminaryNames,
        $q : ng.IQService
    ) {
        super(adapter, adhConfig, adhHttp, adhPermissions, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/CommentCreate.html";
    }
}

export var adhCommentListing = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentListing.html",
        scope: {
            path: "@",
        },
        controller: ["adhTopLevelState", "$location", (
            adhTopLevelState : AdhTopLevelState.TopLevelState,
            $location : ng.ILocationService
        ) : void => {
            adhTopLevelState.setCameFrom($location.url());
        }]
    };
};

/**
 * Directive which checks whether an ExternalResource exists for the given
 * poolPath and key. ExternalResource is a commentable.
 *
 * If not, it is created on the fly.
 *
 * If it exists, the corresponding comment listing is created.
 */
export var adhCreateOrShowCommentListing = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        template: "<adh-comment-listing data-ng-if=\"display\" data-path=\"{{commentablePath}}\"></adh-comment-listing>",
        scope: {
            poolPath: "@",
            key: "@"
        },
        controller: ["adhDone", "adhHttp", "adhPreliminaryNames", "adhUser", "$scope", (
            adhDone,
            adhHttp : AdhHttp.Service<any>,
            adhPreliminaryNames : AdhPreliminaryNames,
            adhUser : AdhUser.User,
            $scope
        ) : void => {

            $scope.display = false;
            var commentablePath = $scope.poolPath + $scope.key + "/";

            var setScope = (path) => {
                $scope.display = true;
                $scope.commentablePath = path;
            };

            // create commentable if it doesn't exist yet
            // REFACT: Add Filter "name": $scope.key - this requires name index to be enabled in the backend
            adhHttp.get($scope.poolPath, {
                "content_type": RIExternalResource.content_type
            }).then(
                (result) => {
                    if (_.contains(result.data[SIPool.nick].elements, commentablePath)) {
                        setScope(commentablePath);
                    } else {
                        var unwatch = $scope.$watch(() => adhUser.loggedIn, (loggedIn) => {
                            if (loggedIn) {
                                var externalResource = new RIExternalResource({preliminaryNames: adhPreliminaryNames, name: $scope.key});
                                return adhHttp.post($scope.poolPath, externalResource).then((obj) => {
                                    if (obj.path !== commentablePath) {
                                        console.log("Created object has wrong path (internal error)");
                                    }
                                })["finally"](() => {
                                    // If the post didn't succeed, somebody else will probably already
                                    // have posted the resource. The error can thus be ignored.
                                    setScope(commentablePath);
                                    unwatch();
                                });
                            }
                        });
                    }
                },
                (msg) => {
                    console.log("Could not query given postPool");
                }
            ).then(adhDone);
        }]
    };
};
