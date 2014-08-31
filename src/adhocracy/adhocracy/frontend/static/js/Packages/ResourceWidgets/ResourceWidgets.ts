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

// import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");

import AdhHttp = require("../Http/Http");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");


export enum Mode {display, edit};


export var resourceWrapper = ($q : ng.IQService) => {
    return {
        restrict: "E",
        link: (scope : ng.IScope) => {
            var resourcePromises : ng.IPromise<ResourcesBase.Resource[]>[] = [];

            var resetResourcePromises = (arg?) => {
                resourcePromises = [];
                return arg;
            };

            scope.$on("registerResourceDirective", (ev, promise) => {
                ev.stopPropagation();
                resourcePromises.push(promise);
            });

            scope.$on("triggerSubmit", (ev) => {
                ev.stopPropagation();

                scope.$broadcast("submit");
                $q.all(resourcePromises)
                    .then(resetResourcePromises)
                    .then((resourceLists) => _.reduce(resourceLists, (a : any[], b) => a.concat(b)))
                    .then((resources) => console.log(resources));  // FIXME do deep post
            });

            scope.$on("triggerCancel", (ev) => {
                ev.stopPropagation();
                scope.$broadcast("cancel");
            });

            scope.$on("triggerSetMode", (ev, mode : Mode) => {
                ev.stopPropagation();
                resetResourcePromises();
                scope.$broadcast("setMode", mode);
            });
        }
    };
};


export interface IResourceWidgetScope extends ng.IScope {
    mode : Mode;
    path : string;
    edit() : void;
    submit() : ng.IAngularEvent;
    cancel() : ng.IAngularEvent;
    delete() : ng.IAngularEvent;
}

export class ResourceWidget<R extends ResourcesBase.Resource> {
    private deferred : ng.IDeferred<R[]>;
    public templateUrl : string;

    constructor(
        public adhHttp : AdhHttp.Service<any>,
        public adhPreliminaryNames : AdhPreliminaryNames,
        public $q : ng.IQService
    ) {
        this.deferred = this.$q.defer();
    }

    public createDirective() : ng.IDirective {
        var self : ResourceWidget<R> = this;

        return {
            restrict: "E",
            templateUrl: self.templateUrl,
            scope: {
                mode: "@",
                path: "@"
            },
            link: (scope : IResourceWidgetScope) => {
                scope.mode = scope.mode || Mode.display;  // FIXME: untested

                scope.$on("setMode", (ev, mode : Mode) => self.setMode(scope, mode));
                scope.$on("triggerDelete", (ev, path : string) => self._handleDelete(scope, path));
                scope.$on("$delete", () => self.deferred.resolve([]));
                scope.$on("submit", () => self._provide(scope)
                    .then((resources) => self.deferred.resolve(resources)));

                scope.$on("cancel", () => {
                    if (scope.mode === Mode.edit) {
                        return self.update(scope).then(() => {
                            self.setMode(scope, Mode.display);
                        });
                    } else {
                        return self.$q.when();
                    }
                });

                scope.edit = () => self.setMode(scope, Mode.edit);
                scope.submit = () => scope.$emit("triggerSubmit");
                scope.cancel = () => scope.$emit("triggerCancel");
                scope.delete = () => scope.$emit("triggerDelete", scope.path);

                self.update(scope);
            }
        };
    }

    setMode(scope : IResourceWidgetScope, mode? : string) : void;
    setMode(scope : IResourceWidgetScope, mode? : Mode) : void;
    public setMode(scope, mode) {
        var self : ResourceWidget<R> = this;

        if (typeof mode === "string") {
            mode = Mode[mode];
        } else if (typeof mode === "undefined") {
            mode = Mode.display;
        }

        self.deferred.resolve([]);
        if (mode === Mode.edit) {
            self.deferred = self.$q.defer();
            scope.$emit("registerResourceDirective", self.deferred.promise);
        }
        scope.mode = mode;
    }

    public update(scope : IResourceWidgetScope) : ng.IPromise<void> {
        var self : ResourceWidget<R> = this;

        if (self.adhPreliminaryNames.isPreliminary(scope.path)) {
            return self.$q.when();
        } else {
            return self.adhHttp.get(scope.path)
                .then((resource : R) => self._update(scope, resource));
        }
    }

    /**
     * Handle delete events from children.
     */
    public _handleDelete(scope : IResourceWidgetScope, path : string) : ng.IPromise<void> {
        throw "not implemented";
    }

    /**
     * Update scope from resource.
     */
    public _update(scope : IResourceWidgetScope, resource : R) : ng.IPromise<void> {
        throw "not implemented";
    }

    /**
     * Create resource(s) from scope.
     *
     * If the widget represents a versionable and scope.path
     * is preliminary, this function must also provide an item.
     */
    public _provide(scope : IResourceWidgetScope) : ng.IPromise<R[]> {
        throw "not implemented";
    }
}
