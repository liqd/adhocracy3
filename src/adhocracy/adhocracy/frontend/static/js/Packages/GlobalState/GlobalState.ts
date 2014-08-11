import AdhEventHandler = require("../EventHandler/EventHandler");

/**
 * GlobalState service for managing global state.
 *
 * This service is used to interact with the general state of the
 * application.  In the UI, this state is represented in the moving
 * columns widget.  This state is also what should be encoded in the
 * URL.
 */
export class GlobalState {
    private eventHandler : AdhEventHandler.EventHandler;

    constructor(adhEventHandlerClass : typeof AdhEventHandler.EventHandler) {
        this.eventHandler = new adhEventHandlerClass();
    }

    public setFocus(column : number) : void {
        this.eventHandler.trigger("setFocus", column);
    }

    public onSetFocus(fn : (column : number) => void) : void {
        this.eventHandler.on("setFocus", fn);
    }
}


export var movingColumns = (globalState) => {
    return {
        link: (scope, element) => {
            globalState.onSetFocus((column : number) : void => {
                // This is likely to change in the future.
                // So do not spend too much time interpreting this.
                if (column <= 1) {
                    element.removeClass("is-detail");
                } else if (column === 2) {
                    element.addClass("is-detail");
                }
            });
        }
    };
};


/**
 * A simple focus switcher that can be used until we have a proper widget for this.
 */
export var adhFocusSwitch = (globalState) => {
    return {
        restrict: "E",
        template: "<a href=\"\" ng-click=\"switchFocus()\">X</a>",
        link: (scope) => {
            var column : number = 1;
            scope.switchFocus = () => {
                column = column === 1 ? 2 : 1;
                globalState.setFocus(column);
            };
        }
    };
};
