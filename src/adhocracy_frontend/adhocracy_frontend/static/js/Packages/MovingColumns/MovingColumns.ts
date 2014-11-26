import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export var movingColumns = (
    topLevelState : AdhTopLevelState.Service
) => {
    return {
        link: (scope, element, attrs) => {
            var cls;

            var move = (newCls) => {
                if (topLevelState.get("space") === attrs["space"]) {
                    if (newCls !== cls) {
                        element.removeClass(cls);
                        element.addClass(newCls);
                        cls = newCls;
                    }
                }
            };

            // FIXME: these do not really belong here
            topLevelState.on("content2Url", (url : string) => {
                scope.content2Url = url;
            });
            topLevelState.on("proposalUrl", (url : string) => {
                scope.proposalUrl = url;
            });
            topLevelState.on("commentableUrl", (url : string) => {
                scope.commentableUrl = url;
            });

            topLevelState.on("movingColumns", move);
        }
    };
};


/**
 * A simple focus switcher that can be used until we have a proper widget for this.
 */
export var adhFocusSwitch = (topLevelState : AdhTopLevelState.Service) => {
    return {
        restrict: "E",
        template: "<a href=\"\" ng-click=\"switchFocus()\">X</a>",
        link: (scope) => {
            scope.switchFocus = () => {
                var currentState = topLevelState.get("movingColumns");

                if (currentState.split("-")[1] === "show") {
                    topLevelState.set("movingColumns", "is-collapse-show-show");
                } else {
                    topLevelState.set("movingColumns", "is-show-show-hide");
                }
            };
        }
    };
};


export var moduleName = "adhMovingColumns";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        .directive("adhMovingColumns", ["adhTopLevelState", movingColumns])
        .directive("adhFocusSwitch", ["adhTopLevelState", adhFocusSwitch]);
};
