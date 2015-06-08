/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
import AdhAbuse = require("../Abuse/Abuse");
import AdhComment = require("../Comment/Comment");
import AdhHttp = require("../Http/Http");
import AdhListing = require("../Listing/Listing");
import AdhSPDDocument = require("../spdDocument/spdDocument");
import AdhMovingColumns = require("../MovingColumns/MovingColumns");
import AdhPermissions = require("../Permissions/Permissions");
import AdhResourceArea = require("../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");
import AdhUser = require("../User/User");

// var pkgLocation = "/spdWorkbench";

export var moduleName = "adhSPDWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuse.moduleName,
            AdhComment.moduleName,
            AdhHttp.moduleName,
            AdhListing.moduleName,
            AdhSPDDocument.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName,
            AdhUser.moduleName
        ]);
};
