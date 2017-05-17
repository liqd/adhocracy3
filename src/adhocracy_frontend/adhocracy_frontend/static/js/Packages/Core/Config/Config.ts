/// <reference path="../../../../lib2/types/angular.d.ts"/>
/// <reference path="../../../../lib2/types/leaflet.d.ts"/>

/* tslint:disable:variable-name */

/**
 * The configuration is actually created by the server and provided
 * as a json file at `/config.json`.  It is then injected
 * as a service.
 *
 * This module only holds the interface for type-checking.
 */

export interface IService {
    rest_url : string;
    rest_platform_path : string;
    canonical_url : string;
    redirect_url : string;
    pkg_path : string;
    ws_url : string;
    embedded : boolean;
    trusted_domains : string[];
    locale : string;
    support_email? : string;
    support_url? : string;
    captcha_enabled : boolean;
    captcha_url : string;
    anonymize_enabled : boolean;
    embed_only : boolean;
    hide_header : boolean;
    mercator_platform_path: string;
    financial_plan_url_de?: string;
    financial_plan_url_en?: string;
    site_name : string;
    netiquette_url : string;
    cachebust : boolean;
    cachebust_suffix : string;
    debug : boolean;
    terms_url : {
        en : string;
        de : string;
    };
    piwik_enabled : string;
    piwik_host : string;
    piwik_site_id : string;
    piwik_use_cookies : boolean;
    piwik_track_user_id : boolean;
    map_tile_url : string;
    map_tile_options : L.TileLayerOptions;
    service_konto_login_url? : string;
    service_konto_help_url? : string;
}
