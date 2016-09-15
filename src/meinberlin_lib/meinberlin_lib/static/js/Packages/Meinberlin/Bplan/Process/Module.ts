import * as AdhHttpModule from "../../../Http/Module";
import * as AdhPreliminaryNamesModule from "../../../PreliminaryNames/Module";
import * as AdhEmbedModule from "../../../Embed/Module";
import * as AdhAngularHelpers from "../../../AngularHelpers/Module";

import * as AdhEmbed from "../../../Embed/Embed";

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
