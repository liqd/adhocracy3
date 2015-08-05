/// <reference path="../../../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>

import AdhConfig = require("../../../Config/Config");
import AdhDocument = require("../../../Document/Document");
import AdhHttp = require("../../../Http/Http");
import AdhMapping = require("../../../Mapping/Mapping");
import AdhMovingColumns = require("../../../MovingColumns/MovingColumns");
import AdhPermissions = require("../../../Permissions/Permissions");
import AdhProcess = require("../../../Process/Process");
import AdhResourceArea = require("../../../ResourceArea/ResourceArea");
import AdhTopLevelState = require("../../../TopLevelState/TopLevelState");
import AdhUtil = require("../../../Util/Util");

import RIAlexanderplatzProcess = require("../../../../Resources_/adhocracy_meinberlin/resources/alexanderplatz/IProcess");
import RIGeoDocument = require("../../../../Resources_/adhocracy_core/resources/document/IGeoDocument");
import RIGeoDocumentVersion = require("../../../../Resources_/adhocracy_core/resources/document/IGeoDocumentVersion");
import RIGeoProposal = require("../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposal");
import RIGeoProposalVersion = require("../../../../Resources_/adhocracy_core/resources/proposal/IGeoProposalVersion");
import RIParagraph = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraph");
import RIParagraphVersion = require("../../../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion");
import SIParagraph = require("../../../../Resources_/adhocracy_core/sheets/document/IParagraph");
import SILocationReference = require("../../../../Resources_/adhocracy_core/sheets/geo/ILocationReference");
import SIMultiPolygon = require("../../../../Resources_/adhocracy_core/sheets/geo/IMultiPolygon");

var pkgLocation = "/MeinBerlin/Alexanderplatz/Workbench";


export var workbenchDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
            scope.$on("$destroy", adhTopLevelState.bind("tab", scope));
        }
    };
};

export var getProcessPolygon = (
    adhHttp : AdhHttp.Service<any>
) => (processUrl : string) : angular.IPromise<any> => {
    return adhHttp.get(processUrl).then((resource) => {
        var locationUrl = resource.data[SILocationReference.nick].location;
        return adhHttp.get(locationUrl).then((location) => {
            return location.data[SIMultiPolygon.nick].coordinates[0][0];
        });
    });
};

export var processDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProcessDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.$on("$destroy", adhTopLevelState.bind("tab", scope));
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");

            scope.proposalType = RIGeoProposalVersion.content_type;
            scope.documentType = RIGeoDocumentVersion.content_type;
            scope.shared.isShowMap = true;

            scope.showMap = (isShowMap) => {
                scope.shared.isShowMap = isShowMap;
            };

            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    getProcessPolygon(adhHttp)(processUrl).then((polygon) => {
                        scope.polygon = polygon;
                    });
                }
            });
        }
    };
};

export var documentDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "documentUrl"]);
            adhPermissions.bindScope(scope, () => AdhUtil.parentPath(scope.documentUrl), "documentItemOptions");

            scope.setCameFrom = () => {
                adhTopLevelState.setCameFrom();
            };
        }
    };
};

export var proposalDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalDetailColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
            adhPermissions.bindScope(scope, () => AdhUtil.parentPath(scope.proposalUrl), "proposalItemOptions");
        }
    };
};

export var documentCreateColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    getProcessPolygon(adhHttp)(processUrl).then((polygon) => {
                        scope.polygon = polygon;
                    });
                }
            });
        }
    };
};

export var documentEditColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrl
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "documentUrl"]);
            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    getProcessPolygon(adhHttp)(processUrl).then((polygon) => {
                        scope.polygon = polygon;
                    });
                }
            });

            scope.cancel = () => {
                var url = adhResourceUrl(AdhUtil.parentPath(scope.documentUrl));
                adhTopLevelState.goToCameFrom(url);
            };
        }
    };
};

export var proposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalCreateColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl"]);
        }
    };
};

export var proposalEditColumnDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalEditColumn.html",
        require: "^adhMovingColumn",
        link: (scope, element, attrs, column : AdhMovingColumns.MovingColumnController) => {
            column.bindVariablesAndClear(scope, ["processUrl", "proposalUrl"]);
        }
    };
};


export var moduleName = "adhMeinBerlinAlexanderplatzWorkbench";

export var register = (angular) => {
    var processType = RIAlexanderplatzProcess.content_type;

    angular
        .module(moduleName, [
            AdhDocument.moduleName,
            AdhMapping.moduleName,
            AdhMovingColumns.moduleName,
            AdhPermissions.moduleName,
            AdhProcess.moduleName,
            AdhResourceArea.moduleName,
            AdhTopLevelState.moduleName
        ])
        .config(["adhProcessProvider", (adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templateFactories[processType] = ["$q", ($q : angular.IQService) => {
                return $q.when("<adh-mein-berlin-alexanderplatz-workbench></adh-mein-berlin-alexanderplatz-workbench>");
            }];
        }])
        .config(["adhResourceAreaProvider", (adhResourceAreaProvider : AdhResourceArea.Provider) => {
            adhResourceAreaProvider
                // documents tab
                .default(RIAlexanderplatzProcess, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "documents"
                })
                .default(RIAlexanderplatzProcess, "create_document", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "documents"
                })
                .specific(RIAlexanderplatzProcess, "create_document", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (resource : RIAlexanderplatzProcess) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    }])
                .defaultVersionable(RIGeoDocument, RIGeoDocumentVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "documents"
                })
                .specificVersionable(RIGeoDocument, RIGeoDocumentVersion, "", processType, "", [
                    () => (item : RIGeoDocument, version : RIGeoDocumentVersion) => {
                        return {
                            documentUrl: version.path
                        };
                    }])
                .defaultVersionable(RIGeoDocument, RIGeoDocumentVersion, "edit", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "documents"
                })
                .specificVersionable(RIGeoDocument, RIGeoDocumentVersion, "edit", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (item : RIGeoDocument, version : RIGeoDocumentVersion) => {
                        return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {
                                    documentUrl: version.path
                                };
                            }
                        });
                    }])
                .defaultVersionable(RIParagraph, RIParagraphVersion, "comments", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show",
                    tab: "documents"
                })
                .specificVersionable(RIParagraph, RIParagraphVersion, "comments", processType, "", [
                    () => (item : RIParagraph, version : RIParagraphVersion) => {
                        var documentUrl = _.last(_.sortBy(version.data[SIParagraph.nick].documents));
                        return {
                            commentableUrl: version.path,
                            commentCloseUrl: documentUrl,
                            documentUrl: documentUrl
                        };
                    }])

                // proposals tab
                .default(RIAlexanderplatzProcess, "proposals", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "proposals"
                })
                .default(RIAlexanderplatzProcess, "create_proposal", processType, "", {
                    space: "content",
                    movingColumns: "is-show-hide-hide",
                    tab: "proposals"
                })
                .specific(RIAlexanderplatzProcess, "create_proposal", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (resource : RIAlexanderplatzProcess) => {
                        return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {};
                            }
                        });
                    }])
                .defaultVersionable(RIGeoProposal, RIGeoProposalVersion, "", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "proposals"
                })
                .specificVersionable(RIGeoProposal, RIGeoProposalVersion, "", processType, "", [
                    () => (item : RIGeoProposal, version : RIGeoProposalVersion) => {
                        return {
                            proposalUrl: version.path
                        };
                    }])
                .defaultVersionable(RIGeoProposal, RIGeoProposalVersion, "edit", processType, "", {
                    space: "content",
                    movingColumns: "is-show-show-hide",
                    tab: "proposals"
                })
                .specificVersionable(RIGeoProposal, RIGeoProposalVersion, "edit", processType, "", [
                    "adhHttp", (adhHttp : AdhHttp.Service<any>) => (item : RIGeoProposal, version : RIGeoProposalVersion) => {
                        return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                            if (!options.POST) {
                                throw 401;
                            } else {
                                return {
                                    proposalUrl: version.path
                                };
                            }
                        });
                    }])
                .defaultVersionable(RIGeoProposal, RIGeoProposalVersion, "comments", processType, "", {
                    space: "content",
                    movingColumns: "is-collapse-show-show",
                    tab: "proposals"
                })
                .specificVersionable(RIGeoProposal, RIGeoProposalVersion, "comments", processType, "", [
                    () => (item : RIGeoProposal, version : RIGeoProposalVersion) => {
                        return {
                            commentableUrl: version.path,
                            commentCloseUrl: version.path,
                            proposalUrl: version.path
                        };
                    }]);
        }])
        .config(["adhMapDataProvider", (adhMapDataProvider : AdhMapping.MapDataProvider) => {
            adhMapDataProvider.icons["document"] = {
                className: "icon-board-pin",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
            adhMapDataProvider.icons["document-selected"] = {
                className: "icon-board-pin is-active",
                iconAnchor: [20, 39],
                iconSize: [40, 40]
            };
        }])
        .directive("adhMeinBerlinAlexanderplatzWorkbench", ["adhConfig", "adhTopLevelState", workbenchDirective])
        .directive("adhMeinBerlinAlexanderplatzProcessColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", "adhHttp", processDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", documentDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalDetailColumn", ["adhConfig", "adhPermissions", proposalDetailColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentCreateColumn", ["adhConfig", "adhHttp", documentCreateColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalCreateColumn", ["adhConfig", proposalCreateColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzDocumentEditColumn", [
            "adhConfig", "adhHttp", "adhTopLevelState", "adhResourceUrlFilter", documentEditColumnDirective])
        .directive("adhMeinBerlinAlexanderplatzProposalEditColumn", ["adhConfig", proposalEditColumnDirective]);
};
