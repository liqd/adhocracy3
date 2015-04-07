/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import _ = require("lodash");

import AdhConfig = require("../Config/Config");

var pkgLocation = "/Tabs";


export interface ITabScope extends angular.IScope {
    active : boolean;
    heading : string;
    select() : void;
}

export interface ITabsetScope extends angular.IScope {
    tabs : ITabScope[];
}

export class TabSetController {
    constructor(private $scope : ITabsetScope) {
        this.$scope.tabs = [];
    }

    public select(selectedTab : ITabScope) {
        _.forEach(this.$scope.tabs, (tab : ITabScope) => {
            if (tab.active && tab !== selectedTab) {
                tab.active = false;
            }
        });
        selectedTab.active = true;
    }

    public addTab(tab : ITabScope) {
        this.$scope.tabs.push(tab);

        // we can"t run the select function on the first tab
        // since that would select it twice
        if (this.$scope.tabs.length === 1) {
            tab.active = true;
        } else if (tab.active) {
            this.select(tab);
        }
    }

    public removeTab(tab : ITabScope) {
        var index = this.$scope.tabs.indexOf(tab);

        // Select a new tab if the tab to be removed is selected and not destroyed
        if (tab.active && this.$scope.tabs.length > 1) {
            // If this is the last tab, select the previous tab. else, the next tab.
            var newActiveIndex = (index === this.$scope.tabs.length - 1) ? index - 1 : index + 1;
            this.select(this.$scope.tabs[newActiveIndex]);
        }
        this.$scope.tabs.splice(index, 1);
    }
}

export var tabsetDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        scope: {},
        transclude: true,
        templateUrl: adhConfig.pkg_path + pkgLocation + "/tabset.html",
        controller: ["$scope", TabSetController]
    };
};

export var tabDirective = (adhConfig : AdhConfig.IService) => {
    return {
        require: "^tabset",
        restrict: "E",
        transclude: true,
        templateUrl: adhConfig.pkg_path + pkgLocation + "/tab.html",
        scope: {
            active: "=?",
            heading: "@"
        },
        link: (scope : ITabScope, element, attrs, tabsetCtrl : TabSetController) => {
            scope.select = () => {
                tabsetCtrl.select(scope);
            };

            tabsetCtrl.addTab(scope);

            if (scope.active) {
                tabsetCtrl.select(scope);
            }

            scope.$on("$destroy", () => {
                tabsetCtrl.removeTab(scope);
            });
        }
    };
};


export var moduleName = "adhTabs";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("tabset", ["adhConfig", tabsetDirective])
        .directive("tab", ["adhConfig", tabDirective]);
};
