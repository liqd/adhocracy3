import AdhAngularHelpersModule = require("../AngularHelpers/Module");
import AdhBadgeModule = require("../Badge/Module");
import AdhHttpModule = require("../Http/Module");
import AdhLocaleModule = require("../Locale/Module");
import AdhMovingColumnsModule = require("../MovingColumns/Module");
import AdhPermissionsModule = require("../Permissions/Module");
import AdhResourceAreaModule = require("../ResourceArea/Module");
import AdhTopLevelStateModule = require("../TopLevelState/Module");

import AdhCredentialsModule = require("./CredentialsModule");
import AdhUserModule = require("./Module");

import AdhTopLevelState = require("../TopLevelState/TopLevelState");

import AdhUserViews = require("./Views");


export var moduleName = "adhUserViews";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhCredentialsModule.moduleName,
            AdhLocaleModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhHttpModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhUserModule.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("login", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/Login.html"
                    };
                })
                .when("password_reset", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/PasswordReset.html",
                        reverse: (data) => {
                            return {
                                path: data["_path"],
                                search: {
                                    path: data["path"]
                                }
                            };
                        }
                    };
                })
                .when("create_password_reset", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/CreatePasswordReset.html"
                    };
                })
                .when("register", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/Register.html"
                    };
                })
                .when("activate", ["adhConfig", "adhUser", "adhDone", "$rootScope", "$location", AdhUserViews.activateArea]);
        }])
        .config(["adhResourceAreaProvider", AdhUserViews.registerRoutes()])
        .directive("adhListUsers", ["adhCredentials", "adhConfig", AdhUserViews.userListDirective])
        .directive("adhUserListItem", ["adhConfig", AdhUserViews.userListItemDirective])
        .directive("adhUserProfile", [
            "adhConfig",
            "adhCredentials",
            "adhHttp",
            "adhPermissions",
            "adhTopLevelState",
            "adhUser",
            "adhGetBadges",
            AdhUserViews.userProfileDirective])
        .directive("adhLogin", ["adhConfig", "adhUser", "adhTopLevelState", "adhShowError", AdhUserViews.loginDirective])
        .directive("adhPasswordReset", [
            "adhConfig", "adhHttp", "adhUser", "adhTopLevelState", "adhShowError", AdhUserViews.passwordResetDirective])
        .directive("adhCreatePasswordReset", [
            "adhConfig",
            "adhCredentials",
            "adhHttp",
            "adhUser",
            "adhTopLevelState",
            "adhShowError",
            AdhUserViews.createPasswordResetDirective])
        .directive("adhRegister", [
            "adhConfig", "adhCredentials", "adhUser", "adhTopLevelState", "adhShowError", AdhUserViews.registerDirective])
        .directive("adhUserIndicator", ["adhConfig", "adhResourceArea", "adhTopLevelState", "$location", AdhUserViews.indicatorDirective])
        .directive("adhUserMeta", ["adhConfig", "adhResourceArea", "adhGetBadges", AdhUserViews.metaDirective])
        .directive("adhUserMessage", ["adhConfig", "adhHttp", AdhUserViews.userMessageDirective])
        .directive("adhUserDetailColumn", ["adhPermissions", "adhConfig", AdhUserViews.userDetailColumnDirective])
        .directive("adhUserListingColumn", ["adhConfig", AdhUserViews.userListingColumnDirective])
        .directive("adhUserManagementHeader", ["adhConfig", AdhUserViews.adhUserManagementHeaderDirective]);
};
