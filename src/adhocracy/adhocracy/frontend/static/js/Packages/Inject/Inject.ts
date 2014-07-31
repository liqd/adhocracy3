/**
 * This is a drop-in replacement for ng-transclude.
 *
 * While the included template in ng-transclude inherits the scope from the
 * controller context where it is defined, the inject directive will use the
 * scope from where it is used.
 *
 * Due to a scoping bug in Angular < 1.2.18 it was possible to use transclude
 * instead of inject to get similar results.
 *
 * The inject directive is directly taken from
 * https://github.com/angular/angular.js/issues/7874#issuecomment-47647528
 */

export var factory = () => {
    return {
        link: ($scope, $element, $attrs, controller, $transclude) => {
            if (!$transclude) {
                throw "Illegal use of inject directive in the template! " +
                    "No parent directive that requires a transclusion found.";
            }
            var innerScope = $scope.$new();
            $transclude(innerScope, (clone) => {
                $element.empty();
                $element.append(clone);
                $element.on("$destroy", () => {
                    innerScope.$destroy();
                });
            });
        }
    };
};
