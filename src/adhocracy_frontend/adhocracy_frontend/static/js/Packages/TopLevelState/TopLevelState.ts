/**
 * TopLevelState service for managing top level state.
 *
 * This service is used to interact with the general state of the
 * application.  In the UI, this state is represented in the moving
 * columns widget.  This state is also what should be encoded in the
 * URL.
 *
 * The state consists of the state of each column and the currently
 * focused column. Note that the "column" metaphor is derived from the
 * moving columns widget. This does not need to be represented by
 * actual columns in every implementation.
 *
 * Only focus and the state of content2 column are currently
 * implemented.
 */

import AdhEventHandler = require("../EventHandler/EventHandler");


export class Service {
    private eventHandler : AdhEventHandler.EventHandler;
    private movingColumns : string;
    private space : string;

    constructor(
        adhEventHandlerClass : typeof AdhEventHandler.EventHandler,
        private $location : ng.ILocationService,
        private $rootScope : ng.IScope
    ) {
        var self = this;

        this.eventHandler = new adhEventHandlerClass();
        this.movingColumns = "is-show-hide-hide";
        this.space = "content";

        this.watchUrlParam("movingColumns", (state) => {
            self.setMovingColumns(state);
        });
    }

    private watchUrlParam(key, fn) {
        var self = this;

        self.$rootScope.$watch(() => self.$location.search()[key], (n, o) => {
            // to not break the back button, we do not directly push another history entry
            self.$location.replace();
            fn(n, o);
        });
    }

    public setContent2Url(url : string) : void {
        this.eventHandler.trigger("setContent2Url", url);
    }

    public onSetContent2Url(fn : (url : string) => void) : void {
        this.eventHandler.on("setContent2Url", fn);
    }

    // FIXME: {set,get}CameFrom should be worked into the class
    // doc-comment, but I don't feel I understand that comment well
    // enough to edit it.  (also, the entire toplevelstate thingy will
    // be refactored soon in order to get state mgmt with link support
    // right.  see /docs/source/api/frontend-state.rst)
    //
    // Open problem: if the user navigates away from the, say, login,
    // and the cameFrom stack will never be cleaned up...  how do we
    // clean it up?

    private cameFrom : string;

    public setCameFrom(path : string) : void {
        this.cameFrom = path;
    }

    public getCameFrom() : string {
        return this.cameFrom;
    }

    public clearCameFrom() : void {
        this.cameFrom = undefined;
    }

    public redirectToCameFrom(_default? : string) : void {
        var cameFrom = this.getCameFrom();
        if (typeof cameFrom !== "undefined") {
            this.$location.url(cameFrom);
        } else if (typeof _default !== "undefined") {
            this.$location.url(_default);
        }
    }

    public setMovingColumns(state : string) : void {
        this.movingColumns = state;
        this.eventHandler.trigger("setMovingColumns", this.movingColumns);
    }

    public onMovingColumns(fn : (state) => void) : void {
        this.eventHandler.on("setMovingColumns", fn);
    }

    public getMovingColumns() {
        return this.movingColumns;
    }

    public setSpace(space : string) : void {
        this.space = space;
        this.eventHandler.trigger("setSpace", space);
    }

    public onSetSpace(fn : (space : string) => void) : void {
        this.eventHandler.on("setSpace", fn);
    }

    public getSpace() : string {
        return this.space;
    }
}

export var movingColumns = (
    topLevelState : Service
) => {
    var cls;

    return {
        link: (scope, element) => {
            var space = topLevelState.getSpace();

            var move = (newCls) => {
                if (topLevelState.getSpace() !== space) {
                    return;
                };
                if (typeof newCls === "undefined") {
                    return;
                };

                if (newCls !== cls) {
                    element.removeClass(cls);
                    element.addClass(newCls);
                    cls = newCls;
                }
            };

            topLevelState.onSetContent2Url((url : string) => {
                scope.content2Url = url;
            });

            topLevelState.onMovingColumns(move);
            move(topLevelState.getMovingColumns());
        }
    };
};


/**
 * A simple focus switcher that can be used until we have a proper widget for this.
 */
export var adhFocusSwitch = (topLevelState : Service) => {
    return {
        restrict: "E",
        template: "<a href=\"\" ng-click=\"switchFocus()\">X</a>",
        link: (scope) => {
            scope.switchFocus = () => {
                var currentState = topLevelState.getMovingColumns();

                if (currentState.split("-")[1] === "show") {
                    topLevelState.setMovingColumns("is-collapse-show-show");
                } else {
                    topLevelState.setMovingColumns("is-show-show-hide");
                }
            };
        }
    };
};


export var spaces = (
    topLevelState : Service
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<adh-inject></adh-inject>",
        link: (scope) => {
            // FIXME: also save content2Url
            var movingColumns = {};
            topLevelState.onSetSpace((space : string) => {
                movingColumns[scope.currentSpace] = topLevelState.getMovingColumns();
                scope.currentSpace = space;
                topLevelState.setMovingColumns(movingColumns[space]);
            });
            scope.currentSpace = topLevelState.getSpace();
        }
    };
};


export var spaceSwitch = (
    topLevelState : Service
) => {
    return {
        restrict: "E",
        template: "<a href=\"\" data-ng-click=\"setSpace('content')\">Content</a>" +
            "<a href=\"\" data-ng-click=\"setSpace('user')\">User</a>",
        link: (scope) => {
            scope.setSpace = (space : string) => {
                topLevelState.setSpace(space);
            };
        }
    };
};


export var moduleName = "adhTopLevelState";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEventHandler.moduleName
        ])
        .service("adhTopLevelState", ["adhEventHandlerClass", "$location", "$rootScope", Service])
        .directive("adhMovingColumns", ["adhTopLevelState", movingColumns])
        .directive("adhFocusSwitch", ["adhTopLevelState", adhFocusSwitch])
        .directive("adhSpaces", ["adhTopLevelState", spaces])
        .directive("adhSpaceSwitch", ["adhTopLevelState", spaceSwitch]);
};
