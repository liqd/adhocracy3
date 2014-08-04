import AdhConfig = require("../Config/Config");

var pkgLocation = "/Comment";

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
