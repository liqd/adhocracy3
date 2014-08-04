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

export class Comment {
    public createDirective(adhConfig : AdhConfig.Type) {
        return {
            restrict: "E",
            templateUrl: adhConfig.pkg_path + pkgLocation + "/Comment.html",
            scope: {
                path: "="
            },
            controller: [() => {
                return;
            }]
        };
    }
}
