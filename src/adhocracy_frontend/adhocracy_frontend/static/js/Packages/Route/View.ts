export var factory = ($compile : ng.ICompileService) => {
    return {
        restrict: "E",
        scope: {
            template: "@"
        },
        link: (scope, element) => {
            scope.$watch("template", (template) => {
                element.html(template);
                $compile(element.contents())(scope);
            });
        }
    };
};
