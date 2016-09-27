/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../Config/Config";
var pkgLocation = "/Core/Markdown";


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
            isMarkdown: "=",
            title: "@",
            maxlength: "=",
            didClickSave: "&"
        },
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/InlineEditableMarkdown.html",
        link: (scope) => {
            scope.isEditing = false;
            // Sorry for the hubhub with the watches here, but the template has multiple levels of child
            // scopes (due to nested ng-if's), so we need a way to ensure that we can get a notification back
            // here when the value is changed deep inside. data = {} is that way.
            // REFACT would be nice to enhance scope with $bind()...
            scope.data = { parsetext: scope.parsetext };
            scope.$watch("parsetext", (parsetext) => {
                scope.isEmpty = !parsetext || 0 === parsetext.trim().length;
                scope.data.parsetext = parsetext;
            });
            scope.$watch("data.parsetext", (parsetext) => {
                scope.parsetext = parsetext;
            });
            scope.startEditing = () => {
                if (scope.isEditable) {
                    scope.originalMarkdown = scope.parsetext;
                    scope.isEditing = true;
                }
            };
            scope.cancelEditing = () => {
                scope.parsetext = scope.originalMarkdown;
                scope.isEditing = false;
            };
            scope.saveChanges = () => {
                scope.didClickSave();
                scope.isEditing = false;
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
