/// <reference path="../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../Config/Config";
var pkgLocation = "/Markdown";


export var parseMarkdown = (adhConfig : AdhConfig.IService, markdownit) => {
    return {
        scope: {
            parsetext: "="
        },
        restrict: "E",
        link: (scope, element) => {
            var md = new markdownit();

            element.html("<div class=\"markdown-rendered\"></div>");
            var wrapper = element.find(".markdown-rendered");

            scope.$watch("parsetext", (newValue : string) => {
                if (newValue) {
                    wrapper.html(md.render(newValue));
                } else {
                    wrapper.html("");
                }
            });
        }
    };
};

// REFACT would be really nice to use the markdown editor that SDI already has
// see: https://simplemde.com
export var inlineEditableMarkdownDirective = (
    adhConfig: AdhConfig.IService
) => {
    return {
        scope: {
            parsetext: "=",
            isEditable: "=",
            title: "@",
            saveChangesCallback: "&saveChanges" // gets the changed markdown as 'markdown' keyword argument
            // REFACT consider to use the binding to get the data out and then only notify via didClickSave() instead of saveChangesCallback(markdown)
        },
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/InlineEditableMarkdown.html",
        link: (scope) => {
            scope.startEditing = () => {
                scope.isEditing = true;
            };
            scope.cancelEditing = () => {
                scope.isEditing = false;
            };
            scope.saveChanges = () => {
                scope.saveChangesCallback({markdown: scope.parsetext});
                scope.cancelEditing();
            };
        }
    };
};

export var testMarkdown = (adhConfig: AdhConfig.IService) => {
    return {
        restrict: "E",
        template: "<textarea ng-model=\"data.parsetext\" cols=\"50\" rows=\"10\"></textarea>" +
        "<adh-parse-markdown ng-if=\"data.parsetext\" parsetext=\"data.parsetext\"></adh-parse-markdown>",
        link: (scope) => {
            scope.data = {};
        }
    };
};
