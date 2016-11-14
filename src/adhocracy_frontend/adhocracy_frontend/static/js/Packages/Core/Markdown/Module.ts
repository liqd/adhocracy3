import * as AdhMarkdown from "./Markdown";


export var moduleName = "adhMarkdown";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhParseMarkdown", ["adhConfig", "markdownit", AdhMarkdown.parseMarkdown])
        .directive("adhInlineEditableMarkdown", ["adhConfig", AdhMarkdown.inlineEditableMarkdownDirective])
        .directive("adhTestParseMarkdown", ["adhConfig", AdhMarkdown.testMarkdown]);
};
