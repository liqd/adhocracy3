import AdhConfig = require("../Config/Config");
import AdhResource = require("../../Resources");

var pkgLocation = "/Comment";

export interface ICommentAdapter<T extends AdhResource.Content<any>> {
    create() : T;
    content(res : T) : string;
    content(res : T, value : string) : T;
    refersTo(res : T) : string;
    refersTo(res : T, value : string) : T;
    creator(red : T) : string;
}

export class CommentCreate {
    constructor(private adapter : ICommentAdapter<any>) {}

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self : CommentCreate = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentCreate.html",
            scope: {},
            controller: ["$scope", "adhHttp", "adhDone", ($scope, adhHttp, adhDone) => {
                $scope.errors = [];
            }]
        };
    }
}

export class CommentDetail {
    constructor(private adapter : ICommentAdapter<any>) {}

    public createDirective(adhConfig : AdhConfig.Type) {
        var _self : CommentDetail = this;

        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/CommentDetail.html",
            scope: {
                path: "=",
                viemode: "="
            },
            controller: [() => {
                return;
            }]
        };
    }
}
