import * as _ from "lodash";

import * as AdhBadge from "../Badge/Badge";
import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhMovingColumns from "../MovingColumns/MovingColumns";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

import * as SIBadgeable from "../../../Resources_/adhocracy_core/sheets/badge/IBadgeable";

var pkgLocation = "/Core/ResourceActions";


export class Modals {
    public modal : string;
    public alerts : {[id : number]: {message : string, mode : string}};
    private lastId : number;

    constructor(protected $timeout) {
        this.lastId = 0;
        this.alerts = {};
    }

    public alert(message : string, mode : string = "info", duration : number = 3000) : void {
        var id = this.lastId++;
        this.$timeout(() => this.removeAlert(id), duration);

        this.alerts[id] = {
            message: message,
            mode: mode
        };
    }

    public removeAlert(id : number) : void {
        delete this.alerts[id];
    }

    public showModal(key : string) : void {
        this.modal = key;
    }

    public hideModal(key? : string) : void {
        if (typeof key === "undefined" || this.modal === key) {
            this.modal = undefined;
        }
    }

    public toggleModal(key : string, condition? : boolean) : void {
        if (condition || (typeof condition === "undefined" && this.modal !== key)) {
            this.modal = key;
        } else if (this.modal === key) {
            this.modal = undefined;
        }
    }

    public clear() : void {
        this.alerts = {};
        this.modal = undefined;
    }
}

export var resourceDropdownDirective = (
    $timeout : angular.ITimeoutService,
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        scope: {
            resourcePath: "@",
            // If the resource is versionable, some actions should be
            // performed on the item instead. This is why we need to
            // know the itemPath. If the resource is not versionable,
            // itemPath should be the same as resourcePath.
            itemPath: "@",
            deleteRedirectUrl: "@?",
            assignBadges: "=?",
            share: "=?",
            hide: "=?",
            resourceWidgetDelete: "=?",
            print: "=?",
            report: "=?",
            cancel: "=?",
            edit: "=?",
            image: "=?",
            moderate: "=?",
            messaging: "=?",
            modals: "=?",
            settings: "=?"
        },
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ResourceDropdown.html",
        link: (scope, element) => {
            scope.data = {
                isShowDropdown: false,
            };

            scope.modals = new Modals($timeout);
            adhPermissions.bindScope(scope, () => scope.resourcePath, "options");
            adhPermissions.bindScope(scope, () => scope.itemPath, "itemOptions");

            scope.$watch("resourcePath", () => {
                scope.modals.clear();
            });

            scope.canEdit = () => {
                if (scope.resourcePath === scope.itemPath) {
                    return scope.options.PUT;
                } else {
                    return scope.itemOptions.POST;
                }
            };

            scope.toggleDropdown = () => {
                scope.data.isShowDropdown = !scope.data.isShowDropdown;
            };

            scope.showDropdownMenu = () => {
                return !scope.modals.modal && _.isEmpty(scope.modals.alerts);
            };

            scope.id = "resourceDropdown" + Math.random();

            // some jQuery that closes the dropdown when the user clicks somewhere else:
            element.focusout(() => {
                $timeout(() => {
                    if (!$.contains(element[0], document.activeElement)) {
                        scope.data.isShowDropdown = false;
                    }
                });
            });
            scope.$on("$delete", () => {
                element.off("focusout");
            });
        }
    };
};


export var resourceActionsDirective = (
    $timeout : angular.ITimeoutService,
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    var directive = resourceDropdownDirective($timeout, adhConfig, adhPermissions);
    directive.scope["createDocument"] = "=?";
    directive.templateUrl = adhConfig.pkg_path + pkgLocation + "/ResourceActions.html";
    return directive;
};


export var modalActionDirective = () => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"toggle();\">" +
            "<ng-transclude></ng-transclude> {{ label | translate }}</a>",
        scope: {
            class: "@",
            modals: "=",
            modal: "@",
            label: "@",
            toggleDropdown: "=?"
        },
        link: (scope) => {
            scope.toggle = () => {
                scope.modals.toggleModal(scope.modal);
            };
        }
    };
};

export var assignBadgesActionDirective = (
    adhConfig: AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a data-ng-if=\"assignableBadgePaths.length\" class=\"{{class}}\" href=\"\"" +
            "data-ng-click=\"assignBadges();\"><ng-transclude></ng-transclude> " +
            "{{ 'TR__MANAGE_BADGE_ASSIGNMENTS' | translate }}</a>",
        scope: {
            resourcePath: "@",
            class: "@",
            modals: "=",
            toggleDropdown: "=?"
        },
        link: (scope) => {
            var badgeAssignmentPoolPath;
            scope.$watch("resourcePath", (resourcePath) => {
                if (resourcePath) {
                    adhHttp.get(resourcePath).then((badgeable) => {
                        badgeAssignmentPoolPath = SIBadgeable.get(badgeable).post_pool;
                    });
                }
            });
            adhPermissions.bindScope(scope, () => badgeAssignmentPoolPath, "badgeAssignmentPoolOptions", {importOptions: false});
            scope.$watch("badgeAssignmentPoolOptions", (rawOptions) => {
                if (rawOptions) {
                    scope.assignableBadgePaths = AdhBadge.getAssignableBadgePaths(rawOptions);
                }
            });

            scope.assignBadges = () => {
                scope.modals.toggleModal("badges");
                scope.toggleDropdown();
            };
        }
    };
};

export var hideActionDirective = (
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrlFilter,
    $translate,
    $window : Window
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"hide();\"><ng-transclude></ng-transclude> " +
            "{{ 'TR__HIDE' | translate }}</a>",
        scope: {
            resourcePath: "@",
            class: "@",
            redirectUrl: "@?",
        },
        link: (scope, element) => {
            scope.hide = () => {
                return $translate("TR__ASK_TO_CONFIRM_HIDE_ACTION").then((question) => {
                    if ($window.confirm(question)) {
                        return adhHttp.hide(scope.resourcePath).then(() => {
                            var url = scope.redirectUrl;
                            if (!url) {
                                var processUrl = adhTopLevelState.get("processUrl");
                                url = processUrl ? adhResourceUrlFilter(processUrl) : "/";
                            }
                            adhTopLevelState.goToCameFrom(url);
                        });
                    }
                });
            };
        }
    };
};

export var resourceWidgetDeleteActionDirective = () => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"delete();\"><ng-transclude></ng-transclude> " +
            "{{ 'TR__DELETE' | translate }}</a>",
        require: "^adhMovingColumn",
        scope: {
            resourcePath: "@",
            class: "@"
        },
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            scope.delete = () => {
                column.$broadcast("triggerDelete", scope.resourcePath);
            };
        }
    };
};

export var printActionDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    $window : Window
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"print();\"><ng-transclude></ng-transclude> " +
            "{{ 'TR__PRINT' | translate }}</a>",
        require: "?^adhMovingColumn",
        scope: {
            class: "@"
        },
        link: (scope, element, attrs, column? : AdhMovingColumns.MovingColumnController) => {
            scope.print = () => {
                if (column) {
                    // only the focused column is printed
                    column.focus();
                }
                $window.print();
            };
        }
    };
};

export var viewActionDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrl,
    $location : angular.ILocationService
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"link();\"><ng-transclude></ng-transclude> {{ label | translate }}</a>",
        scope: {
            resourcePath: "@",
            class: "@",
            label: "@",
            view: "@",
        },
        link: (scope) => {
            scope.link = () => {
                adhTopLevelState.setCameFrom();
                var url = adhResourceUrl(scope.resourcePath, scope.view);
                $location.url(url);
            };
        }
    };
};

export var cancelActionDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrl
) => {
    return {
        restrict: "E",
        transclude: true,
        template: "<a class=\"{{class}}\" href=\"\" data-ng-click=\"cancel();\"><ng-transclude></ng-transclude> " +
            "{{ 'TR__CANCEL' | translate }}</a>",
        scope: {
            resourcePath: "@",
            class: "@"
        },
        link: (scope) => {
            scope.cancel = () => {
                if (!scope.resourcePath) {
                    scope.resourcePath = adhTopLevelState.get("processUrl");
                }
                var url = adhResourceUrl(scope.resourcePath);
                adhTopLevelState.goToCameFrom(url);
            };
        }
    };
};
