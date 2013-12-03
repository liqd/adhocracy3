import Types = require('Adhocracy/Types');
import Obviel = require('Adhocracy/Obviel');

export function isInfixOf(needle, hay) {
    return hay.indexOf(needle) !== -1;
};

export function parentPath(url) {
    return url.substring(0, url.lastIndexOf("/"));
};

export function post(url : string,
                     json : Types.Content,
                     done : (c : Types.Content) => void,
                     fail : Function)
{
    $.ajax(url, {
        type: "POST",
        data: JSON.stringify(Obviel.jsonBeforeSend(json)),
        dataType: "json",
        contentType: "application/json"
    }).done(function(response : Types.Content) {
        done(Obviel.jsonAfterReceive(response, undefined));
    }).fail(fail);
};

export function postx(url : string,
                      json : Types.Content,
                      headers : Object,
                      done : (c : Types.Content) => void,
                      fail : Function)
{
    $.ajax(url, {
        type: "POST",
        data: JSON.stringify(Obviel.jsonBeforeSend(json)),
        headers : headers,
        dataType: "json",
        contentType: "application/json"
    }).done(function(response : Types.Content) {
        done(Obviel.jsonAfterReceive(response, undefined));
    }).fail(fail);
};

export function get(url : string,
                    done : (c : Types.Content) => void,
                    fail : Function)
{
    $.get(url)
        .done(function(response : Types.Content) {
            done(Obviel.jsonAfterReceive(response, undefined));
        })
        .fail(fail);
};
