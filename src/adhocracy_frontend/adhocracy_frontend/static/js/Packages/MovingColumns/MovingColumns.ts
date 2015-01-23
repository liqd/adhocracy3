import _ = require("lodash");

import AdhConfig = require("../Config/Config");
import AdhTopLevelState = require("../TopLevelState/TopLevelState");

export var pkgLocation = "/MovingColumns";


export var movingColumns = (
    adhTopLevelState : AdhTopLevelState.Service,
    $timeout,
    $window
) => {
    return {
        link: (scope, element) => {
            var cls : string;
            var fontSize : number = parseInt(element.css("font-size"), 10);

            var maxShowWidth = 55 * fontSize;
            var minShowWidth = 35 * fontSize;
            var collapseWidth = 3 * fontSize;
            var spacing = Math.ceil(0.3 * fontSize);

            var clearStates = (element) => {
                element.removeClass("is-show");
                element.removeClass("is-collapse");
                element.removeClass("is-hide");
            };

            // if there is not enough space, collapse all but one column.
            var responsiveClass = (cls : string) : string => {
                if ($($window).width() < 2 * minShowWidth + collapseWidth) {
                    var s = "is";
                    var parts = cls.split("-");

                    var focus = parseInt(adhTopLevelState.get("focus"), 10);
                    if (isNaN(focus)) {
                        focus = parts.lastIndexOf("show") - 1;
                    }

                    for (var i = 0; i < 3; i++) {
                        if (i > focus) {
                            s += "-hide";
                        } else if (i === focus) {
                            s += "-show";
                        } else {
                            s += "-collapse";
                        }
                    }

                    return s;
                } else {
                    return cls;
                }
            };

            var resize = () : void => {
                if (typeof cls === "undefined") {
                    return;
                }

                var parts = responsiveClass(cls).split("-");

                var collapseCount : number = parts.filter((v) => v === "collapse").length;
                var showCount : number = parts.filter((v) => v === "show").length;
                var totalWidth : number = element.outerWidth();
                var totalCollapseWidth : number = collapseCount * collapseWidth;
                var totalSpacingWidth : number = (collapseCount + showCount - 1) * spacing;
                var showWidth : number = (totalWidth - totalCollapseWidth - totalSpacingWidth) / showCount;
                showWidth = Math.min(showWidth, maxShowWidth);

                var totalShowWidthWithSpacing = showCount * showWidth + (showCount - 1) * spacing;
                var offset : number = (totalWidth - totalShowWidthWithSpacing) / 2 - collapseCount * (collapseWidth + spacing);
                offset = Math.max(offset, 0);

                for (var i = 0; i < 3; i++) {
                    var child = element.children().eq(i);
                    child.css({left: offset});
                    clearStates(child);
                    switch (parts[i + 1]) {
                        case "show":
                            child.addClass("is-show");
                            child.attr("aria-visible", "true");
                            child.outerWidth(showWidth);
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
                    if (parts[i] !== "hide" && parts[i + 1] !== "hide") {
                        offset += spacing;
                    }
                }
            };

            var resizeNoTransition = () => {
                var transition = element.children().css("transition");
                element.children().css("transition", "none");
                resize();
                $timeout(() => {
                    element.children().css("transition", transition);
                }, 1);
            };

            $($window).resize(resizeNoTransition);

            var move = (newCls) => {
                if (newCls !== cls) {
                    element.removeClass(cls);
                    element.addClass(newCls);
                    cls = newCls;
                    resize();
                }
            };

            adhTopLevelState.on("movingColumns", move);
            adhTopLevelState.on("focus", resize);
            adhTopLevelState.on("space", () => _.defer(resizeNoTransition));
        }
    };
};


export class MovingColumnController {
    private lastId : number;

    constructor(protected $timeout : ng.ITimeoutService, protected $scope) {
        $scope.ctrl = this;
        $scope.alerts = {};
        $scope.shared = {};

        this.lastId = 0;
    }

    public alert(message : string, mode : string = "info", duration : number = 3000) : void {
        var id = this.lastId++;
        this.$timeout(() => this.removeAlert(id), duration);

        this.$scope.alerts[id] = {
            message: message,
            mode: mode
        };
    }

    public removeAlert(id : number) : void {
        delete this.$scope.alerts[id];
    }

    public showOverlay(key : string) : void {
        this.$scope.overlay = key;
    }

    public hideOverlay(key? : string) : void {
        if (typeof key === "undefined" || this.$scope.overlay === key) {
            this.$scope.overlay = undefined;
        }
    }

    public toggleOverlay(key : string, condition? : boolean) : void {
        if (condition || (typeof condition === "undefined" && this.$scope.overlay !== key)) {
            this.$scope.overlay = key;
        } else if (this.$scope.overlay === key) {
            this.$scope.overlay = undefined;
        }
    }

    public showSidebar() : void {
        this.toggleSidebar(true);
    }

    public hideSidebar() : void {
        this.toggleSidebar(false);
    }

    public toggleSidebar(condition? : boolean) : void {
        if (typeof condition === "undefined") {
            condition = !this.$scope.showSidebar;
        }
        this.$scope.showSidebar = condition;
    }
}


export var movingColumnDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        scope: true,
        transclude: true,
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MovingColumn.html",
        controller: ["$timeout", "$scope", MovingColumnController]
    };
};


export var moduleName = "adhMovingColumns";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        .directive("adhMovingColumn", ["adhConfig", movingColumnDirective])
        .directive("adhMovingColumns", ["adhTopLevelState", "$timeout", "$window", movingColumns]);
};
