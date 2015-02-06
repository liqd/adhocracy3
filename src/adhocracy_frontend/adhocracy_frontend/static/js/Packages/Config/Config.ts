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
    pkg_path : string;
    ws_url : string;
    embedded : boolean;
    trusted_domains : string[];
    locale : string;
    support_email : string;
    custom : {[key : string]: string};
    site_name : string;
    cachebust : boolean;
    cachebust_suffix : string;
    debug : boolean;
    terms_url : string;
    piwik_enabled : string;
    piwik_host : string;
    piwik_site_id : string;
    piwik_use_cookies : boolean;
    piwik_track_user_id : boolean;
}
