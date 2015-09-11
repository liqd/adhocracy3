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
 * In addition to a modified scoping, the inject directive also allows to
 * have multiple transcluded elements.
 *
 * Example: Listing template:
 *
 *     <div class="Listing">
 *        <inject data-transclusion-id="add-form-id"></inject>
 *        <ol>
 *            <li ng-repeat="element in elements">
 *                <inject data-transclusion-id="element-id"></inject>
 *            </li>
 *        </ol>
 *     </div>
 *
 * Some other template that uses listing:
 *
 *     <listing>
 *         <div data-ng-switch="transclusionId">
 *             <adh-proposal-version-new data-ng-switch-when="add-form-id"></adh-proposal-version-new>
 *             <adh-proposal-detail data-path="element" data-ng-switch-when="element-id"></adh-proposal-detail>
 *         </div>
 *     </listing>
 *
 * The purpose of data-transclusion-id is a bit confusing until you
 * think of it as function application with named arguments: the
 * definition of the listing template has the form (in tsc syntax):
 *
 *     var listing = (add-form-id, element-id) => { render("<div class...</div>"); }
 *
 * And the application of this template has the form:
 *
 *     listing("<adh-proposal-version-new ...", "<adh-proposal-detail ...");
 *
 * The bug in Angular < 1.2.18 gave us dynamic scoping for the
 * `element` variable in the example: The scope is opened in the
 * definition of Listing, but accessed in the application.  A better
 * solution would be to do this with something like a lambda
 * abstraction as well, but we haven't gotten around figuring out how
 * quite yet.
 *
 * The inject directive is based on the one from
 * https://github.com/angular/angular.js/issues/7874#issuecomment-47647528
 */

// FIXME: Injection does not allow for the template author to control
// the name of scope variables passed to injected template snippets.
// Instead of something like:
//
// <listing element="row">
//   <element path="{{row}}"></element>
// </listing>
//
// She has to write:
//
// <listing>
//   <element path="{{element}}"></element>
// </listing>
//
// and implicitly know that Listing propagates the identifier
// ``element`` to the element's scope.

export var factory = () => {
    return {
        restrict: "EAC",
        link: ($scope, $element, $attrs, controller, $transclude) => {
            if (!$transclude) {
                throw "Illegal use of inject directive in the template! " +
                    "No parent directive found that requires a transclusion.";
            }
            var innerScope = $scope.$new();
            innerScope.transclusionId = $element.data("transclusion-id");
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
