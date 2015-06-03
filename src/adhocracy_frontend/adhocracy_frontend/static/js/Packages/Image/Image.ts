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
        .module(moduleName, [])
        .filter("adhImageUri", imageUriFilter);
};
