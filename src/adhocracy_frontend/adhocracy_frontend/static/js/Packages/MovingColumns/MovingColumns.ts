import AdhTopLevelState = require("../TopLevelState/TopLevelState");


export var movingColumns = (
    topLevelState : AdhTopLevelState.Service,
    $timeout,
    $window
) => {
    return {
        link: (scope, element, attrs) => {
            var cls;

            var clearStates = (element) => {
                element.removeClass("is-show");
                element.removeClass("is-collapse");
                element.removeClass("is-hide");
            };

            var resize = () => {
                var fontSize : number = parseInt(element.css("font-size"), 10);

                var collapseCount : number = cls.split("-").filter((v) => v === "collapse").length;
                var showCount : number = cls.split("-").filter((v) => v === "show").length;

                var totalWidth : number = element.width();
                var collapseWidth : number = 3 * fontSize;
                var showWidth : number = (totalWidth - collapseCount * collapseWidth) / showCount;

                var offset : number = 0;

                for (var i = 2; i >= 0; i--) {
                    var child = element.children().eq(i);
                    child.css({right: offset});
                    clearStates(child);
                    switch (cls.split("-")[i + 1]) {
                        case "show":
                            child.addClass("is-show");
                            child.attr("aria-visible", "true");
                            child.width(showWidth);
                            offset += showWidth;
                            break;
                        case "collapse":
                            child.addClass("is-collapse");
                            child.attr("aria-visible", "false");
                            child.width(collapseWidth);
                            offset += collapseWidth;
                            break;
                        case "hide":
                            child.addClass("is-hide");
                            child.attr("aria-visible", "false");
                            child.width(0);
                    }
                }
            };

            $($window).resize(() => {
                var transition = element.children().css("transition");
                element.children().css("transition", "none");
                resize();
                $timeout(() => {
                    element.children().css("transition", transition);
                }, 1);
            });

            var move = (newCls) => {
                if (topLevelState.get("space") === attrs["space"]) {
                    if (newCls !== cls) {
                        element.removeClass(cls);
                        element.addClass(newCls);
                        cls = newCls;
                        resize();
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
        .directive("adhMovingColumns", ["adhTopLevelState", "$timeout", "$window", movingColumns])
        .directive("adhFocusSwitch", ["adhTopLevelState", adhFocusSwitch]);
};
