/**
 * This package provides directives that represent resources.
 *
 * These directives provide a generic interface for creating, displaying,
 * editing and deleting resources with minimal additional effort.
 *
 * Each resourceWidget takes care of its own resources.  It can communicate
 * with other resourceWidgets py emitting events.  These events are catched
 * by a resourceWrapper that in turn broadcasts it to all its children.
 *
 * The following event types exist:
 *
 * setMode / triggerSetMode
 * : set the mode (display/edit) to the first parameter given with this event.
 *
 * cancel / triggerCancel
 * : change from edit mode to display mode; discard all unsaved changes
 *
 * submit / triggerSubmit
 * : the resourceWrapper waits for all registered resourcePromises. When
 *   they are ready, it uses deepPost to post all updates.
 *
 * registerResourceDirective
 * : is used by resourceWidgets to register a promise with the resourceWrapper
 *   that can be resolved on submit.  Instead of unregistering, the promise
 *   may simply be resolved with an empty list.
 */

import ResourcesBase = require("../../ResourcesBase");

import AdhHttp = require("../Http/Http");
import AdhEventHandler = require("../EventHandler/EventHandler");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");


export enum Mode {display, edit};


export interface IResourceWrapperController {
    registerResourceDirective(promise : ng.IPromise<ResourcesBase.Resource[]>) : void;
    triggerSubmit() : ng.IPromise<void>;
    triggerCancel() : void;
    triggerSetMode(mode : Mode) : void;
    eventHandler : AdhEventHandler.EventHandler;
}

export var resourceWrapper = () => {
    return {
        restrict: "E",
        controller: ["$scope", "$attrs", "$q", "adhEventHandlerClass", function(
            $scope : ng.IScope,
            $attrs : ng.IAttributes,
            $q : ng.IQService,
            adhEventHandlerClass
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

            self.triggerSubmit = () => {
                self.eventHandler.trigger("submit");
                return $q.all(resourcePromises)
                    .then(resetResourcePromises)
                    .then((resourceLists) => _.reduce(resourceLists, (a : any[], b) => a.concat(b)))
                    .then((resources) => console.log(resources))  // FIXME do deep post
                    .then(() => self.triggerSetMode(Mode.display))
                    .then(() => triggerCallback("onSubmit"));
            };

            self.triggerCancel = () => {
                self.eventHandler.trigger("cancel");
                triggerCallback("onCancel");
            };

            self.triggerSetMode = (mode : Mode) => {
                resetResourcePromises();
                self.eventHandler.trigger("setMode", mode);
            };
        }]
    };
};


export interface IResourceWidgetScope extends ng.IScope {
    mode : Mode;
    path : string;
    edit() : void;
    submit() : ng.IPromise<void>;
    cancel() : void;
    delete() : void;
}

export interface IResourceWidgetInstance<R extends ResourcesBase.Resource, S extends IResourceWidgetScope> {
    scope : S;
    wrapper : IResourceWrapperController;
    deferred : ng.IDeferred<R[]>
}

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

    setMode(instance : IResourceWidgetInstance<R, S>, mode? : string) : void;
    setMode(instance : IResourceWidgetInstance<R, S>, mode? : Mode) : void;
    public setMode(instance, mode) : void {
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
