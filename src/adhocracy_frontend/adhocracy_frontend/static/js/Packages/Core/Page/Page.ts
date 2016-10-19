import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhResourceArea from "../ResourceArea/ResourceArea";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

import * as ResourcesBase from "../../ResourcesBase";

import RIPage from "../../../Resources_/adhocracy_core/resources/page/IPage";
import * as SIDescription from "../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SITitle from "../../../Resources_/adhocracy_core/sheets/title/ITitle";

var pkgLocation = "/Core/Page";


export var pageDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {},
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("resourceUrl", scope, "path"));

            scope.$watch("path", (path : string) => {
                if (path) {
                    adhHttp.get(path).then((page : ResourcesBase.IResource) => {
                        scope.title = SITitle.get(page).title;
                        scope.description = SIDescription.get(page).description;
                    });
                }
            });
        }
    };
};

export var registerRoutes = (
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider.default(RIPage, "", "", context, {
        space: "page"
    });
};
