import * as AdhEmbedModule from "../Embed/Module";
import * as AdhHttpModule from "../Http/Module";

import * as AdhEmbed from "../Embed/Embed";

import * as Activity from "./Activity";


export var moduleName = "adhActivity";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerDirective("activity-stream");
        }])
        .directive("adhActivityStream", ["adhConfig", "adhHttp", Activity.streamDirective])
        .directive("adhActivity", ["adhConfig", "adhHttp", Activity.activityDirective]);
};
