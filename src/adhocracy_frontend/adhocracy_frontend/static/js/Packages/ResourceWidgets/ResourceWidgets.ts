/**
 * This package provides directives that represent resources.
 *
 * These directives provide a generic interface for creating, displaying,
 * editing and deleting resources with minimal additional effort.
 *
 * Each resourceWidget takes care of its own resources.  There is a single
 * central resourceWrapper that manages communication and also takes care
 * of collecting all generated resources and dispatching an HTTP request
 * on submit.
 *
 * The resourceWidgets can access the resourceWrapper by requiring it and
 * using its controller (see https://docs.angularjs.org/guide/directive#creating-directives-that-communicate).
 * See IResourceWrapperController for a description of the interface.
 */

import ResourcesBase = require("../../ResourcesBase");

import AdhHttp = require("../Http/Http");
import AdhEventHandler = require("../EventHandler/EventHandler");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");


export enum Mode {display, edit};


export interface IResourceWrapperController {
    /**
     * An event handler that is used whenever the resourceWrapper needs to
     * contact the resourceWidgets. The following events are used:
     *
     * setMode
     * : set mode to the passed argument
     *
     * cancel
     * : when in edit mode, reset scope and switch to display mode
     *
     * submit
     * : resolve promise with a list of resources
     */
    eventHandler : AdhEventHandler.EventHandler;

    /**
     * registers a promise that will eventually be resolved with a list of
     * resources on submit.
     */
    registerResourceDirective(promise : ng.IPromise<ResourcesBase.Resource[]>) : void;

    /**
     * triggers a "setMode" event on eventHandler
     */
    triggerSetMode(mode : Mode) : void;

    /**
     * triggers a "cancel" event on eventHandler
     */
    triggerCancel() : void;

    /**
     * triggers a "submit" event on eventHandler. This will cause the
     * resourceWidgets to resolve the promises registered via
     * registerResourceDirective. When all promises have been resolved,
     * all promised resources will be posted to the server via deepPost.
     */
    triggerSubmit() : ng.IPromise<void>;
}

/**
 * Directive that wraps resourceWidgets, manages communication and also takes
 * care of dispatching a HTTP request on submit.
 *
 * You can pass two callbacks to this directive:
 *
 * onSubmit
 * : called after successful submit
 *
 * onCancel
 * : called after cancel
 *
 * Note that these callbacks need to be functions of type () : void in the
 * parent scope.
 */
export var resourceWrapper = () => {
    return {
        restrict: "E",
        controller: ["$scope", "$attrs", "$q", "adhEventHandlerClass", "adhHttp", function(
            $scope : ng.IScope,
            $attrs : ng.IAttributes,
            $q : ng.IQService,
            adhEventHandlerClass,
            adhHttp : AdhHttp.Service<any>
        ) {
            var self : IResourceWrapperController = this;
            var resourcePromises : ng.IPromise<ResourcesBase.Resource[]>[] = [];

            var resetResourcePromises = (arg?) => {
                resourcePromises = [];
                return arg;
            };

            var triggerCallback = (key : string) : void => {
                if (typeof $attrs[key] !== "undefined") {
                    var fn = $scope.$parent[$attrs[key]];
                    fn.call($scope.$parent);
                }
            };

            self.eventHandler = new adhEventHandlerClass();

            self.registerResourceDirective = (promise : ng.IPromise<ResourcesBase.Resource[]>) => {
                resourcePromises.push(promise);
            };

            self.triggerSetMode = (mode : Mode) => {
                resetResourcePromises();
                self.eventHandler.trigger("setMode", mode);
            };

            self.triggerCancel = () => {
                self.eventHandler.trigger("cancel");
                triggerCallback("onCancel");
            };

            self.triggerSubmit = () => {
                self.eventHandler.trigger("submit");
                return $q.all(resourcePromises)
                    .then(resetResourcePromises)
                    .then((resourceLists) => _.reduce(resourceLists, (a : any[], b) => a.concat(b)))
                    .then((resources) => adhHttp.deepPost(resources))
                    .then(() => self.triggerSetMode(Mode.display))
                    .then(() => triggerCallback("onSubmit"));
            };
        }]
    };
};


export interface IResourceWidgetScope extends ng.IScope {
    mode : Mode;
    path : string;

    /**
     * Set mode to "edit"
     */
    edit() : void;

    /**
     * Trigger submit on resourceWrapper.
     */
    submit() : ng.IPromise<void>;

    /**
     * Trigger cancel on resourceWrapper.
     */
    cancel() : void;

    /**
     * Emit an angular "delete" event.
     */
    delete() : void;
}

export interface IResourceWidgetInstance<R extends ResourcesBase.Resource, S extends IResourceWidgetScope> {
    scope : S;
    wrapper : IResourceWrapperController;
    deferred : ng.IDeferred<R[]>
}

/**
 * Abstract base class for all resourceWidgets.
 *
 * This class implements the basic functionality to interact with a
 * resourceWrapper. It is implemented in such a way that most functionality is
 * implemented in widget methods. This way it is easy to extend.
 *
 * Subclasses need to implement _handleDelete, _update, _create and _edit. They
 * must also set templateUrl in the constructor. Additionally, they may extend
 * createDirective to modify the generated directive directly.
 *
 * If a resourceWidget is instantiated without a mode, the mode defaults to
 * "display".
 *
 * A resourceWidget must always be instantiated with a path. If you want to use
 * the widget to create a new resource and therefore do not know its path, you
 * must use a preliminary name (see PreliminaryNames package). The
 * resourceWidget will detect that and behave accordingly (e.g. it will not try
 * to load the resource from the server).
 */
export class ResourceWidget<R extends ResourcesBase.Resource, S extends IResourceWidgetScope> {
    public templateUrl : string;

    constructor(
        public adhHttp : AdhHttp.Service<any>,
        public adhPreliminaryNames : AdhPreliminaryNames,
        public $q : ng.IQService
    ) {}

    public createDirective() : ng.IDirective {
        var self : ResourceWidget<R, S> = this;

        return {
            restrict: "E",
            require: "^adhResourceWrapper",
            templateUrl: self.templateUrl,
            scope: {
                mode: "@",
                path: "@"
            },
            link: (scope : S, element, attrs, wrapper : IResourceWrapperController) => {
                self.link(scope, element, attrs, wrapper);
            }
        };
    }

    public link(scope : S, element, attrs, wrapper : IResourceWrapperController) : IResourceWidgetInstance<R, S> {
        var self : ResourceWidget<R, S> = this;

        var instance : IResourceWidgetInstance<R, S> = {
            scope: scope,
            wrapper: wrapper,
            deferred: self.$q.defer()
        };

        var setModeID = wrapper.eventHandler.on("setMode", (mode : Mode) => self.setMode(instance, mode));
        var submitID = wrapper.eventHandler.on("submit", () => self.provide(instance)
            .then((resources) => instance.deferred.resolve(resources)));

        var cancelID = wrapper.eventHandler.on("cancel", () => {
            if (scope.mode === Mode.edit) {
                return self.update(instance).then(() => {
                    self.setMode(instance, Mode.display);
                });
            } else {
                return self.$q.when();
            }
        });

        scope.$on("triggerDelete", (ev, path : string) => self._handleDelete(instance, path));
        scope.$on("$delete", () => {
            wrapper.eventHandler.off("setMode", setModeID);
            wrapper.eventHandler.off("submit", submitID);
            wrapper.eventHandler.off("cancel", cancelID);
            instance.deferred.resolve([]);
        });

        scope.edit = () => wrapper.triggerSetMode(Mode.edit);
        scope.submit = () => wrapper.triggerSubmit();
        scope.cancel = () => wrapper.triggerCancel();
        scope.delete = () => scope.$emit("triggerDelete", scope.path);

        self.setMode(instance, scope.mode);
        self.update(instance);

        return instance;
    }

    /**
     * Set the mode of a this widget to either "display" or "edit".
     *
     * this method should  not be used directly. You should rather use
     * instance.wrapper.triggerSetMode in order to change the mode on all
     * resourceWidgets in this resourceWrapper.
     */
    private setMode(instance : IResourceWidgetInstance<R, S>, mode? : string) : void;
    private setMode(instance : IResourceWidgetInstance<R, S>, mode? : Mode) : void;
    private setMode(instance, mode) {
        var self : ResourceWidget<R, S> = this;

        if (typeof mode === "string") {
            mode = Mode[mode];
        } else if (typeof mode === "undefined") {
            mode = Mode.display;
        }

        instance.deferred.resolve([]);
        if (mode === Mode.edit) {
            instance.deferred = self.$q.defer();
            instance.wrapper.registerResourceDirective(instance.deferred.promise);
        }
        instance.scope.mode = mode;
    }

    public update(instance : IResourceWidgetInstance<R, S>) : ng.IPromise<void> {
        var self : ResourceWidget<R, S> = this;

        if (self.adhPreliminaryNames.isPreliminary(instance.scope.path)) {
            return self.$q.when();
        } else {
            return self.adhHttp.get(instance.scope.path)
                .then((resource : R) => self._update(instance, resource));
        }
    }

    /**
     * Handle delete events from children.
     */
    public _handleDelete(instance : IResourceWidgetInstance<R, S>, path : string) : ng.IPromise<void> {
        throw "not implemented";
    }

    /**
     * Update scope from resource.
     */
    public _update(instance : IResourceWidgetInstance<R, S>, resource : R) : ng.IPromise<void> {
        throw "not implemented";
    }

    /**
     * Create resource(s) from scope.
     *
     * Calls _create/_edit based on whether scope.path is preliminary.
     */
    public provide(instance : IResourceWidgetInstance<R, S>) : ng.IPromise<R[]> {
        if (this.adhPreliminaryNames.isPreliminary(instance.scope.path)) {
            return this._create(instance);
        } else {
            return this.adhHttp.get(instance.scope.path).then((old) => {
                return this._edit(instance, old);
            });
        }
    }

    /**
     * Initially create resource(s) from scope.
     */
    public _create(instance : IResourceWidgetInstance<R, S>) : ng.IPromise<R[]> {
        throw "not implemented";
    }

    /**
     * Create modified resource(s) from scope.
     */
    public _edit(instance : IResourceWidgetInstance<R, S>, old : R) : ng.IPromise<R[]> {
        throw "not implemented";
    }
}