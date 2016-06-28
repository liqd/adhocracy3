import * as _ from "lodash";

import * as AdhConfig from "../Config/Config";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

export var pkgLocation = "/MovingColumns";


/**
 * Moving Columns directive
 *
 * taking care of showing, hiding and resizing the columns
 */
export var movingColumns = (
    adhTopLevelState : AdhTopLevelState.Service,
    $timeout,
    $window
) => {
    return {
        link: (scope, element, attrs) => {
            var cls : string;
            var fontSize : number = parseInt(element.css("font-size"), 10);
            var maxWidth = 55;
            if (typeof attrs.maxWidth !== "undefined") {
                maxWidth = parseInt(attrs.maxWidth, 10);
            }
            var maxShowWidth = maxWidth * fontSize;
            var minShowWidth = 35 * fontSize;
            var collapseWidth = 2 * fontSize;
            var spacing = Math.ceil(0.3 * fontSize);
            if (typeof attrs.spacing !== "undefined") {
                spacing = parseInt(attrs.spacing, 10);
            }

            var clearStates = (element) => {
                element.removeClass("is-show");
                element.removeClass("is-collapse");
                element.removeClass("is-hide");
                element.removeClass("is-first-visible-child");
                element.removeClass("is-last-visible-child");
                element.removeClass("has-focus");
            };

            var getFocus = (cls : string) : number => {
                var parts = cls.split("-");
                var focus = parseInt(adhTopLevelState.get("focus"), 10);
                if (isNaN(focus)) {
                    focus = parts.lastIndexOf("show") - 1;
                }
                return focus;
            };

            // if there is not enough space, collapse all but one column.
            var responsiveClass = (cls : string) : string => {
                if ($($window).width() < 2 * minShowWidth + collapseWidth) {
                    var s = "is";
                    var focus = getFocus(cls);

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
                var focus = getFocus(cls);

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

                var columns = element.find(".moving-column");

                for (var i = 0; i < 3; i++) {
                    var child = columns.eq(i);
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
                    if (i === focus) {
                        child.addClass("has-focus");
                    }
                    if (parts[i] !== "hide" && parts[i + 1] !== "hide") {
                        offset += spacing;
                    }
                }

                element.find(".moving-column:not(.is-hide):first-child").addClass("is-first-visible-child");
                element.find(".moving-column:not(.is-hide):last").addClass("is-last-visible-child");

            };

            var resizeNoTransition = () => {
                var columns = element.find(".moving-column");
                var transition = columns.css("transition");
                columns.css("transition", "none");
                resize();
                $timeout(() => {
                    columns.css("transition", transition);
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

            scope.$on("$destroy", adhTopLevelState.on("movingColumns", move));
            scope.$on("$destroy", adhTopLevelState.on("focus", resize));
            scope.$on("$destroy", adhTopLevelState.on("space", () => _.defer(resizeNoTransition)));
            scope.$watch(() => element.find(".moving-column").length, resize);
        }
    };
};


/**
 * Moving Column directive
 *
 * Every moving column should be wrapped in an instance of this
 * directive.  It provides common functionality, e.g. alerts and
 * modals via a controller that can be required by subelements.
 *
 * Subelements can inject template code with the following transclusionIds
 * (see AdhInject):
 *
 * -   body
 * -   menu
 * -   collapsed
 * -   modals
 */
export interface IMovingColumnScope extends angular.IScope {
    // the controller with interfaces for alerts, modals, ...
    ctrl : MovingColumnController;

    // an object that can be used to share data between different parts of the column.
    shared;

    // key of the currently active modal or undefined
    modal : string;

    // private
    _alerts : {[id : number]: {
        message : string;
        mode : string;
    }};
}

export class MovingColumnController {
    private lastId : number;

    constructor(
        protected adhTopLevelState : AdhTopLevelState.Service,
        protected $timeout : angular.ITimeoutService,
        public $scope : IMovingColumnScope,
        protected $element : angular.IAugmentedJQuery
    ) {
        $scope.ctrl = this;
        $scope._alerts = {};
        $scope.shared = {};

        this.lastId = 0;
    }

    public focus() : void {
        var index = this.$element.index();
        this.adhTopLevelState.set("focus", index);
    }

    public clear() : void {
        this.$scope._alerts = {};
        this.$scope.modal = undefined;
    }

    public alert(message : string, mode : string = "info", duration : number = 3000) : void {
        var id = this.lastId++;
        this.$timeout(() => this.removeAlert(id), duration);

        this.$scope._alerts[id] = {
            message: message,
            mode: mode
        };
    }

    public removeAlert(id : number) : void {
        delete this.$scope._alerts[id];
    }

    public showModal(key : string) : void {
        this.$scope.modal = key;
    }

    public hideModal(key? : string) : void {
        if (typeof key === "undefined" || this.$scope.modal === key) {
            this.$scope.modal = undefined;
        }
    }

    public toggleModal(key : string, condition? : boolean) : void {
        if (condition || (typeof condition === "undefined" && this.$scope.modal !== key)) {
            this.$scope.modal = key;
        } else if (this.$scope.modal === key) {
            this.$scope.modal = undefined;
        }
    }

    public $broadcast(name : string, ...args : any[]) {
        return this.$scope.$broadcast.apply(this.$scope, arguments);
    }

    /**
     * Bind variables from topLevelState and clear this column whenever one of them changes.
     */
    public bindVariablesAndClear(scope, keys : string[]) : void {
        var self : MovingColumnController = this;

        // NOTE: column directives are typically injected mutliple times
        // with different transcludionIds. But we want to trigger clear() only once.
        var clear = () => {
            if (scope.transclusionId === "body") {
                self.clear();
            }
        };

        clear();

        keys.forEach((key : string) => {
            scope.$on("$destroy", self.adhTopLevelState.on(key, (value) => {
                scope[key] = value;
                clear();
            }));
        });
    }
}


export var movingColumnDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        scope: true,
        replace: true,
        transclude: true,
        templateUrl: adhConfig.pkg_path + pkgLocation + "/MovingColumn.html",
        controller: ["adhTopLevelState", "$timeout", "$scope", "$element", MovingColumnController]
    };
};
