import AdhConfig = require("../Config/Config");
import AdhEmbed = require("../Embed/Embed");
import AdhHttp = require("../Http/Http");

import RIImage = require("../../Resources_/adhocracy_core/resources/image/IImage");
import SIHasAssetPool = require("../../Resources_/adhocracy_core/sheets/asset/IHasAssetPool");
import SIImageMetadata = require("../../Resources_/adhocracy_core/sheets/image/IImageMetadata");
import SIImageReference = require("../../Resources_/adhocracy_core/sheets/image/IImageReference");

var pkgLocation = "/Image";

/**
 * upload mercator proposal image file.  this function can potentially
 * be more general; for now it just handles the Flow object and
 * promises the path of the image resource as a string.
 *
 * as the a3 asset protocol is much simpler than HTML5 file upload, we
 * compose the multi-part mime post request manually (no chunking).
 * The $flow object is just used for meta data retrieval and cleared
 * before it can upload anything.
 *
 * NOTE: this uses several HTML5 APIs so you need to check for
 * compability before using it.
 */
export var uploadImageFactory = (
    adhHttp : AdhHttp.Service<any>
) => (
    poolPath : string,
    flow : Flow,
    contentType : string = RIImage.content_type,
    metadataSheet : string = SIImageMetadata.nick
) : angular.IPromise<string> => {
    if (flow.files.length !== 1) {
        throw "could not upload file: $flow.files.length !== 1";
    }
    var file = flow.files[0].file;

    var bytes = () : any => {
        var func;
        if (file.mozSlice) {
            func = "mozSlice";
        } else if (file.webkitSlice) {
            func = "webkitSlice";
        } else {
            func = "slice";
        }

        return file[func](0, file.size, file.type);
    };

    var formData = new FormData();
    formData.append("content_type", contentType);
    formData.append("data:" + metadataSheet + ":mime_type", file.type);
    formData.append("data:adhocracy_core.sheets.asset.IAssetData:data", bytes());

    return adhHttp.get(poolPath)
        .then((pool) => {
            var postPath : string = pool.data[SIHasAssetPool.nick].asset_pool;
            return adhHttp.postRaw(postPath, formData)
                .then((rsp) => rsp.data.path)
                .catch(<any>AdhHttp.logBackendError);
        });
};


export var addImage = (
    adhHttp : AdhHttp.Service<any>
) => (
    resourcePath : string,
    imagePath : string
) => {
    return adhHttp.get(resourcePath).then((version) => {
        var newVersion = {
            content_type: version.content_type,
            data: {}
        };
        newVersion.data[SIImageReference.nick] = new SIImageReference.Sheet({
            picture: imagePath
        });
        return adhHttp.postNewVersionNoFork(resourcePath, newVersion);
    });
};


export var uploadImageDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhUploadImage,
    flowFactory
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Upload.html",
        scope: {
            poolPath: "@",
            path: "@"
        },
        link: (scope) => {
            scope.$flow = flowFactory.create();

            scope.$flow.on("fileAdded", (file, event) => {
                scope.$flow.files = [file];
                return false;
            });

            scope.submit = () => {
                return adhUploadImage(scope.poolPath, scope.$flow)
                    .then((imagePath : string) => addImage(adhHttp)(scope.path, imagePath));
            };
        }
    };
};

export var imageUriFilter = () => {
    return (path? : string, format : string = "detail") : string => {
        if (path) {
            return path + "/" + format;
        } else {
            return "/static/fallback_" + format + ".jpg";
        }
    };
};


export var moduleName = "adhImage";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbed.moduleName,
            AdhHttp.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("upload-image");
        }])
        .factory("adhUploadImage", ["adhHttp", uploadImageFactory])
        .directive("adhUploadImage", ["adhConfig", "adhHttp", "adhUploadImage", "flowFactory", uploadImageDirective])
        .filter("adhImageUri", imageUriFilter);
};
