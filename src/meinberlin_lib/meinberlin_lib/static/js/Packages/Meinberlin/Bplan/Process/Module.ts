import * as AdhHttpModule from "../../../Core/Http/Module";
import * as AdhPreliminaryNamesModule from "../../../Core/PreliminaryNames/Module";
import * as AdhEmbedModule from "../../../Core/Embed/Module";
import * as AdhAngularHelpers from "../../../Core/AngularHelpers/Module";

import * as AdhEmbed from "../../../Core/Embed/Embed";

import * as Process from "./Process";


export var moduleName = "adhMeinBerlinBplanProcess";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpers.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhPreliminaryNamesModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider
                .registerDirective("meinberlin-bplan-process-create");
        }])
        .directive("adhMeinberlinBplanProcessCreate", [
            "adhConfig", "adhHttp", "adhPreliminaryNames", "adhShowError", "adhSubmitIfValid", "$window", Process.createDirective]);
};
