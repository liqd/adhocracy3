import * as AdhAbuseModule from "../../Core/Abuse/Module";
import * as AdhCommentModule from "../../Core/Comment/Module";
import * as AdhDocumentModule from "../../Core/Document/Module";
import * as AdhEmbedModule from "../../Core/Embed/Module";
import * as AdhHttpModule from "../../Core/Http/Module";
import * as AdhMovingColumnsModule from "../../Core/MovingColumns/Module";
import * as AdhPermissionsModule from "../../Core/Permissions/Module";
import * as AdhResourceActionsModule from "../../Core/ResourceActions/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";
import * as AdhTopLevelStateModule from "../../Core/TopLevelState/Module";

import * as AdhDocument from "../../Core/Document/Document";
import * as AdhEmbed from "../../Core/Embed/Embed";
import * as AdhIdeaCollectionWorkbench from "../../Core/IdeaCollection/Workbench/Workbench";
import * as AdhNames from "../../Core/Names/Names";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";

export var moduleName = "adhMeinberlinCollaborativeText";

export var register = (angular) => {
    var processType = RICollaborativeTextProcess.content_type;

    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhDocumentModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[processType] = "TR__RESOURCE_COLLABORATIVE_TEXT_EDITING";
        }]);
};
