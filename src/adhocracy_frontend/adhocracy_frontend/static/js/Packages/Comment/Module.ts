import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhCredentialsModule = require("../User/Module");
import AdhDateTimeModule = require("../DateTime/Module");
import AdhDoneModule = require("../Done/Module");
import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");
import AdhListingModule = require("../Listing/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhPreliminaryNamesModule = require("../PreliminaryNames/Module");
import AdhRateModule = require("../Rate/Module");
import AdhResourceWidgetsModule = require("../ResourceWidgets/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhListing = require("../Listing/Listing");

import AdhComment = require("./Comment");
import Adapter = require("./Adapter");


export var moduleName = "adhComment";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhCredentialsModule.moduleName,
            AdhDateTimeModule.moduleName,
            AdhDoneModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhListingModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhPreliminaryNamesModule.moduleName,
            AdhRateModule.moduleName,
            AdhResourceWidgetsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhCommentListingPartial",
            ["adhConfig", "adhWebSocket", (adhConfig, adhWebSocket) =>
                new AdhListing.Listing(new Adapter.ListingCommentableAdapter()).createDirective(adhConfig, adhWebSocket)])
        .directive("adhCommentListing", ["adhConfig", "adhTopLevelState", "$location", AdhComment.adhCommentListing])
        .directive("adhCreateOrShowCommentListing", [
            "adhConfig", "adhDone", "adhHttp", "adhPreliminaryNames", "adhCredentials", AdhComment.adhCreateOrShowCommentListing])
        .directive("adhCommentResource", [
            "adhConfig", "adhHttp", "adhPermissions", "adhPreliminaryNames", "adhTopLevelState", "adhRecursionHelper", "$window", "$q",
            (adhConfig, adhHttp, adhPermissions, adhPreliminaryNames, adhTopLevelState, adhRecursionHelper, $window, $q) => {
                var adapter = new Adapter.CommentAdapter();
                var widget = new AdhComment.CommentResource(
                    adapter, adhConfig, adhHttp, adhPermissions, adhPreliminaryNames, adhTopLevelState, $window, $q);
                return widget.createRecursionDirective(adhRecursionHelper);
            }])
        .directive("adhCommentCreate", [
            "adhConfig", "adhHttp", "adhPermissions", "adhPreliminaryNames", "adhTopLevelState", "adhRecursionHelper", "$window", "$q",
            (adhConfig, adhHttp, adhPermissions, adhPreliminaryNames, adhTopLevelState, adhRecursionHelper, $window, $q) => {
                var adapter = new Adapter.CommentAdapter();
                var widget = new AdhComment.CommentCreate(
                    adapter, adhConfig, adhHttp, adhPermissions, adhPreliminaryNames, adhTopLevelState, $window, $q);
                return widget.createRecursionDirective(adhRecursionHelper);
            }])
        .directive("adhCommentColumn", ["adhConfig", AdhComment.commentColumnDirective]);
};
