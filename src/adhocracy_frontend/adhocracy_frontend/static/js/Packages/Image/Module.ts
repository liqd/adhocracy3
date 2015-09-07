import AdhEmbedModule = require("../Embed/Module");
import AdhHttpModule = require("../Http/Module");

import AdhEmbed = require("../Embed/Embed");

import AdhImage = require("./Image");


export var moduleName = "adhImage";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider: AdhEmbed.Provider) => {
            adhEmbedProvider.embeddableDirectives.push("upload-image");
        }])
        .factory("adhUploadImage", ["adhHttp", AdhImage.uploadImageFactory])
        .directive("adhUploadImage", ["adhConfig", "adhHttp", "adhUploadImage", "flowFactory", AdhImage.uploadImageDirective])
        .filter("adhImageUri", AdhImage.imageUriFilter);
};
