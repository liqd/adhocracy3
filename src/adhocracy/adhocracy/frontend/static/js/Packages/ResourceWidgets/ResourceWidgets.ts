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
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");


export enum Mode {display, edit};


export interface IResourceWrapperController {
    registerResourceDirective(promise : ng.IPromise<ResourcesBase.Resource[]>) : void;
    triggerSubmit() : ng.IPromise<void>;
    triggerCancel() : void;
    triggerSetMode(mode : Mode) : void;
}

export var resourceWrapper = () => {
    return {
        restrict: "E",
        controller: ["$scope", "$q", function($scope : ng.IScope, $q : ng.IQService) {
            var self : IResourceWrapperController = this;

            var resourcePromises : ng.IPromise<ResourcesBase.Resource[]>[] = [];

            var resetResourcePromises = (arg?) => {
                resourcePromises = [];
                return arg;
            };

            self.registerResourceDirective = (promise : ng.IPromise<ResourcesBase.Resource[]>) => {
                resourcePromises.push(promise);
            };

            self.triggerSubmit = () => {
                $scope.$broadcast("submit");
                return $q.all(resourcePromises)
                    .then(resetResourcePromises)
                    .then((resourceLists) => _.reduce(resourceLists, (a : any[], b) => a.concat(b)))
                    .then((resources) => console.log(resources))  // FIXME do deep post
                    .then(() => self.triggerSetMode(Mode.display));
            };

            self.triggerCancel = () => {
                $scope.$broadcast("cancel");
            };

            self.triggerSetMode = (mode : Mode) => {
                resetResourcePromises();
                $scope.$broadcast("setMode", mode);
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
                var instance : IResourceWidgetInstance<R, S> = {
                    scope: scope,
                    wrapper: wrapper,
                    deferred: self.$q.defer()
                };

                scope.$on("setMode", (ev, mode : Mode) => self.setMode(instance, mode));
                scope.$on("triggerDelete", (ev, path : string) => self._handleDelete(instance, path));
                scope.$on("$delete", () => instance.deferred.resolve([]));
                scope.$on("submit", () => self._provide(instance)
                    .then((resources) => instance.deferred.resolve(resources)));

                scope.$on("cancel", () => {
                    if (scope.mode === Mode.edit) {
                        return self.update(instance).then(() => {
                            self.setMode(instance, Mode.display);
                        });
                    } else {
                        return self.$q.when();
                    }
                });

                scope.edit = () => wrapper.triggerSetMode(Mode.edit);
                scope.submit = () => wrapper.triggerSubmit();
                scope.cancel = () => wrapper.triggerCancel();
                scope.delete = () => scope.$emit("triggerDelete", scope.path);

                self.setMode(instance, scope.mode);
                self.update(instance);
            }
        };
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
     * If the widget represents a versionable and scope.path
     * is preliminary, this function must also provide an item.
     */
    public _provide(instance : IResourceWidgetInstance<R, S>) : ng.IPromise<R[]> {
        throw "not implemented";
    }
}
