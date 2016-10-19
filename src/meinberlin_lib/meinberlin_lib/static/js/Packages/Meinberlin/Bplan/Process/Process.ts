/// <reference path="../../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../../../Core/Config/Config";
import * as AdhHttp from "../../../Core/Http/Http";
import * as AdhPreliminaryNames from "../../../Core/PreliminaryNames/PreliminaryNames";

import * as ResourcesBase from "../../ResourcesBase";

import * as SIName from "../../../../Resources_/adhocracy_core/sheets/name/IName";
import * as SIProcessPrivateSettings from "../../../../Resources_/adhocracy_meinberlin/sheets/bplan/IProcessPrivateSettings";
import * as SIProcessSettings from "../../../../Resources_/adhocracy_meinberlin/sheets/bplan/IProcessSettings";
import * as SITitle from "../../../../Resources_/adhocracy_core/sheets/title/ITitle";
import * as SIWorkflowAssignment from "../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";
import RIProcess from "../../../../Resources_/adhocracy_meinberlin/resources/bplan/IProcess";

var pkgLocation = "/Meinberlin/Bplan/Process";


export interface IScope {
    poolPath : string;
    errors : any[];
    data : {
        title : string;
        officeWorkerEmail : string;
        startDate : string;
        kind : string;
    };
    showError : any;
    submit() : angular.IPromise<any>;
}


var postCreate = (
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    poolPath : string
) => {
    var process : ResourcesBase.IResource = {
        path: adhPreliminaryNames.nextPreliminary(),
        content_type: RIProcess.content_type,
        data: {},
    };
    process.parent = poolPath;

    process.data[SIName.nick] = new SIName.Sheet({
        name: scope.data.title
    });
    process.data[SITitle.nick] = new SITitle.Sheet({
        title: "Bebauungsplan " + scope.data.title
    });
    process.data[SIProcessSettings.nick] = new SIProcessSettings.Sheet({
        participation_kind: scope.data.kind,
        plan_number: scope.data.title
    });
    process.data[SIProcessPrivateSettings.nick] = new SIProcessPrivateSettings.Sheet({
        office_worker_email: scope.data.officeWorkerEmail
    });
    process.data[SIWorkflowAssignment.nick] = new SIWorkflowAssignment.Sheet({
        state_data: [{
            start_date: scope.data.startDate,
            name: "participate",
            description: ""
        }]
    });

    return adhHttp.deepPost([process]);
};


export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid,
    $window : angular.IWindowService
) => {
    return {
        restrict: "E",
        scope: {
            poolPath: "@"
        },
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        link: (scope, element) => {
            scope.errors = [];
            scope.data = {};
            scope.showError = adhShowError;
            scope.origin = $window.location.origin;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.processForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.poolPath).then((responses) => {
                        scope.resultUrl = responses[0].path;
                    });
                });
            };
        }
    };
};
