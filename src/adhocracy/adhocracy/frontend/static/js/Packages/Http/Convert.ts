import Util = require("../Util/Util");
import MetaApi = require("../MetaApi/MetaApi");
import Resources = require("../../Resources");


/**
 * transform objects on the way in (all request methods)
 */
export var importContent = <Content extends Resources.Content<any>>(response : {data : Content}) : Content => {
    "use strict";

    var obj = response.data;

    if (typeof obj === "object") {
        return obj;
    } else {
        throw ("unexpected type: " + (typeof obj).toString() + " " + obj.toString());
    }

    // FIXME: it would be nice if this function could throw an
    // exception at run-time if the type of obj does not match
    // Content.  however, not only is Content a compile-time entity,
    // but it may very well be based on an interface that has no
    // run-time entity anywhere.  two options:
    //
    // (1) http://stackoverflow.com/questions/24056019/is-there-a-way-to-check-instanceof-on-types-dynamically
    //
    // (2) typescript language feature request! :)
    //
    //
    // the following function would be useful if the problem of
    // turning abstract types into runtime objects could be solved.
    // (for the time being, it has been removed from the Util module
    // where it belongs.)
    //
    //
    //   // in a way another function in the deep* family: check that _super
    //   // has only attributes also available in _sub.  also check recursively
    //   // (if _super has an object attribute, its counterpart in _sub must
    //   // have the same attributes, and so on).
    //
    //   // FIXME: untested!
    //   export function subtypeof(_sub, _super) {
    //       if (typeof _sub !== typeof _super) {
    //           return false;
    //       }
    //
    //       if (typeof(_sub) === "object") {
    //           if (_sub === null || _super === null) {
    //               return true;
    //           }
    //
    //           for (var x in _super) {
    //               if (!(x in _sub)) { return false; }
    //               if (!subtypeof(_sub[x], _super[x])) { return false; }
    //           }
    //       }
    //
    //       return true;
    //   }
};


/**
 * transform batch request response into Content array
 */
export var importBatchContent = <Content extends Resources.Content<any>>(responses : { data : {body : Content}[] }) : Content[] => {
    // FIXME: description files don't appear to support array-typed
    // response bodies.  this might be a good thing (web security and
    // all).  change rest batch spec to wrap array in trivial object?

    return (<any>(responses.data)).map((response) => {
        response.data = response.body;
        delete response.body;
        return importContent(response);
    });
};


/**
 * prepare object for post or put.  remove all fields that are none of
 * editable, creatable, create_mandatory.  remove all sheets that have
 * no fields after this.
 *
 * FIXME: there is a difference between put and post.  namely, fields
 * that may be created but not edited should be treated differently.
 * also, fields with create_mandatory should not be missing from the
 * posted object.
 */
export var exportContent = <Content extends Resources.Content<any>>(adhMetaApi : MetaApi.MetaApiQuery, obj : Content) : Content => {
    "use strict";

    var newobj : Content = Util.deepcp(obj);

    // remove some fields from newobj.data[*] and empty sheets from
    // newobj.data.
    for (var sheetName in newobj.data) {
        if (newobj.data.hasOwnProperty(sheetName)) {
            var sheet : MetaApi.ISheet = newobj.data[sheetName];
            var keepSheet : boolean = false;

            for (var fieldName in sheet) {
                if (sheet.hasOwnProperty(fieldName)) {
                    var fieldMeta : MetaApi.ISheetField = adhMetaApi.field(sheetName, fieldName);

                    if (fieldMeta.editable || fieldMeta.creatable || fieldMeta.create_mandatory) {
                        keepSheet = true;
                    } else {
                        delete sheet[fieldName];
                    }
                }
            }

            if (!keepSheet) {
                delete newobj.data[sheetName];
            }
        }
    }

    delete newobj.path;
    return newobj;
};
