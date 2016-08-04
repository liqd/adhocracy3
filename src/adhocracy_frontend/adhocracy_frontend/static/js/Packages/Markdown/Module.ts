import * as AdhEmbedModule from "../Embed/Module";

import * as AdhEmbed from "../Embed/Embed";

import * as AdhMarkdown from "./Markdown";


export var moduleName = "adhMarkdown";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.registerDirective("test-parse-markdown");
        }])
        .directive("adhParseMarkdown", ["adhConfig", "markdownit", AdhMarkdown.parseMarkdown])
        .directive("adhInlineEditableMarkdown", ["adhConfig", AdhMarkdown.inlineEditableMarkdownDirective])
        .directive("adhTestParseMarkdown", ["adhConfig", AdhMarkdown.testMarkdown]);
};
