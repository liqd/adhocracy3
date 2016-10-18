import * as AdhLocale from "./Locale";


export var moduleName = "adhLocale";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .filter("adhCountryName", AdhLocale.countryName)
        .service("adhWrap", ["$interpolate", AdhLocale.Wrap])
        .directive("adhHtmlTranslate", ["$compile", "$translate", "adhWrap", AdhLocale.htmlTranslateDirective])
        .directive("countrySelect", ["$translate", "adhConfig", AdhLocale.countrySelect]);
};
