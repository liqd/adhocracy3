/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");

export var parsemarkdown = (adhConfig : AdhConfig.IService, markdownit : any) => {
    return {
        scope: {
            parsetext: "="
        },
        restrict: "E",
        link: (scope, element) => {

            var parseMarkdown = (markdown: string): string => {
                var markdownit = require("markdownit");
                    md = new markdownit();
                var result = md.render(markdown);
                return result;
            };

			scope.$watch("parsetext", function(newValue) {
				element.children().remove();
				element.append(parseMarkdown(newValue));
			});
        }
    };
};

export var testmarkdown = (adhConfig: AdhConfig.IService) => {
    return {
        restrict: "E",
        template: "<textarea ng-model=\"data.parsetext\" cols=\"50\" rows=\"10\"></textarea>" +
        "<adh-parse-markdown ng-if=\"data.parsetext\" parsetext=\"data.parsetext\"></adh-parse-markdown>",
        link: (scope) => {
            scope.data = {};
        }
    };
};

export var moduleName = "adhMarkdown";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.registerEmbeddableDirectives(["test-parse-markdown"]);
        }])
        .directive("adhParseMarkdown", ["adhConfig", "markdownit", parsemarkdown])
        .directive("adhTestParseMarkdown", ["adhConfig", testmarkdown]);
};
