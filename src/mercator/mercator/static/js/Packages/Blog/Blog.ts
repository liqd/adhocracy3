import * as AdhConfig from "../Core/Config/Config";
import * as AdhDocument from "../Core/Document/Document";
import * as AdhHttp from "../Core/Http/Http";
import * as AdhPermissions from "../Core/Permissions/Permissions";
import * as AdhPreliminaryNames from "../Core/PreliminaryNames/PreliminaryNames";
import * as AdhUtil from "../Core/Util/Util";

import * as ResourcesBase from "../../ResourcesBase";

import RIDocumentVersion from "../../Resources_/adhocracy_core/resources/document/IDocumentVersion";

var pkgLocation = "/Blog";


export interface IScope extends AdhDocument.IScope {
    titles : {
        value : string;
        title : string;
    }[];
}

export interface IFormScope extends IScope, AdhDocument.IFormScope {
    onSubmit() : void;
}

export var bindPath = (
    $q : angular.IQService,
    adhHttp : AdhHttp.Service
) => {
    var fn = AdhDocument.bindPath($q, adhHttp);

    return (
        scope : IScope,
        pathKey : string = "path"
    ) : Function => {
        scope.titles = [
            {
                value: "road to impact",
                title: "Road to impact"
            },
            {
                value: "heroines and heroes",
                title: "Heroines and heroes"
            },
            {
                value: "impact Story",
                title: "Impact Story"
            },
            {
                value: "take this idea",
                title: "Take this idea!"
            },
            {
                value: "success",
                title: "Success"
            },
            {
                value: "failing forward",
                title: "Failing forward"
            },
            {
                value: "join forces",
                title: "Join forces!"
            },
            {
                value: "anything else",
                title: "Anything else?"
            }
        ];

        return fn(scope, pathKey);
    };
};


export var detailDirective = (
    $q : angular.IQService,
    $window : angular.IWindowService,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid,
    adhUploadImage,
    $translate
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope, element) => {
            var unbind : Function;

            scope.errors = [];
            scope.showError = adhShowError;
            scope.mode = "display";

            adhPermissions.bindScope(scope, () => scope.path);
            adhPermissions.bindScope(scope, () => AdhUtil.parentPath(scope.path), "itemOptions");

            scope.delete = () => {
                return $translate("TR__ASK_TO_CONFIRM_HIDE_ACTION").then((question) => {
                    if ($window.confirm(question)) {
                        var itemPath = AdhUtil.parentPath(scope.path);
                        adhHttp.delete(itemPath)
                            .then(() => {
                                if (typeof scope.onChange !== "undefined") {
                                    scope.onChange();
                                }
                            });
                    }
                });
            };

            scope.edit = () => {
                scope.mode = "edit";
                unbind();
            };

            scope.cancel = () => {
                scope.mode = "display";
                unbind = bindPath($q, adhHttp)(scope);
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return AdhDocument.postEdit(adhHttp, adhPreliminaryNames, adhUploadImage)(
                        scope, scope.documentVersion, scope.paragraphVersions);
                }).then((documentVersion : ResourcesBase.IResource) => {
                    if (typeof scope.onChange !== "undefined") {
                        scope.onChange();
                    }
                });
            };

            unbind = bindPath($q, adhHttp)(scope);
        }
    };
};

export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid,
    adhUploadImage
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@",
            onSubmit: "=?"
        },
        link: (scope : IFormScope, element) => {
            scope.errors = [];
            scope.titles = [
                {
                    value: "road to impact",
                    title: "Road to impact"
                },
                {
                    value: "heroines and heroes",
                    title: "Heroines and heroes"
                },
                {
                    value: "impact Story",
                    title: "Impact Story"
                },
                {
                    value: "take this idea",
                    title: "Take this idea!"
                },
                {
                    value: "success",
                    title: "Success"
                },
                {
                    value: "failing forward",
                    title: "Failing forward"
                },
                {
                    value: "join forces",
                    title: "Join forces!"
                },
                {
                    value: "anything else",
                    title: "Anything else?"
                }
            ];
            scope.data = {
                title: "",
                paragraphs: [{
                    body: "",
                    deleted: false
                }]
            };
            scope.showError = adhShowError;
            scope.showCreateForm = false;

            scope.toggleCreateForm = () => {
                scope.showCreateForm = true;
            };

            scope.cancel = () => {
                scope.data.paragraphs[0].body = "";
                scope.data.title = "";
                scope.documentForm.$setPristine();
                scope.showCreateForm = false;
            };

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.documentForm, () => {
                    return AdhDocument.postCreate(adhHttp, adhPreliminaryNames, adhUploadImage)(scope, scope.path);
                }).then((documentVersion : ResourcesBase.IResource) => {

                    scope.cancel();

                    if (typeof scope.onSubmit !== "undefined") {
                        scope.onSubmit();
                    }
                }, (errors) => {
                    scope.errors = errors;
                });
            };
        }
    };
};

export var listingDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.contentType = RIDocumentVersion.content_type;
        }
    };
};
