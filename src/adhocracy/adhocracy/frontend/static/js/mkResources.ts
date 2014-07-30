/// <reference path="../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../lib/DefinitelyTyped/underscore/underscore.d.ts"/>

/* tslint:disable:no-var-requires */
var http : any = require("http");
var fs : any = require("fs");
var _fs : any = require("node-fs");
var _s : any = require("underscore.string");
/* tslint:enable:no-var-requires */

import u = require("./mkResources/Util");


/***********************************************************************
 * types
 */

interface IMetaApi {
    sheets : { [index: string]: ISheet };
    resources : { [index: string]: IResource };
}

interface ISheet {
    fields : ISheetField[];

    // generated after import
    nick ?: string;
}

interface ISheetField {
    name : string;
    valuetype : string;
    containertype ?: string;
    readable : boolean;
    editable : boolean;
    creatable : boolean;
    create_mandatory : boolean;
    targetsheet : string;
}

interface IResource {
    sheets : string[];
    item_type : string;
    element_types : string[];

    // generated after import
    nick ?: string;
}

interface IModuleDict {
    [index: string]: string;
}

var compileAll : (IMetaApiResponse) => void;

var renderSheet : (string, ISheet, IModuleDict, IMetaApi) => void;
var mkFieldSignatures : (fields : ISheetField[], tab : string, separator : string) => string;
var mkFieldAssignments : (fields : ISheetField[], tab : string) => string;
var enabledFields : (fields : ISheetField[], enableFlags ?: string) => ISheetField[];
var mkSheetSetter : (modulePath : string, fields : ISheetField[], _selfType : string) => string;
var mkSheetGetter : (modulePath : string, _selfType : string) => string;

var renderResource : (string, IResource, IModuleDict, IMetaApi) => void;

var mkSheetName : (string) => string;
var mkHasSheetName : (string) => string;
var mkResourceClassName : (string) => string;
var mkModuleName : (string, metaApi : IMetaApi) => string;
var mkImportStatement : (modulePath : string, relativeRoot : string, metaApi : IMetaApi) => string;
var mkNick : (modulePath : string, metaApi : IMetaApi) => string;
var mkFieldType : (ISheetField) => string;
var mkFlags : (field : ISheetField, comment ?: boolean) => string;

var mkdirForFile : (string) => void;
var pyModuleToTsModule : (string) => string;
var mkRelativeRoot : (source : string) => string;
var canonicalizePath : (string) => string;


/***********************************************************************
 * fetch api
 */

var options = {
    host: "127.0.0.1",
    port: 6541,
    path: "/meta_api/"
};

var callback = (response) => {
    var body : string = "";
    var bodyJs : IMetaApi;

    var cbData = (chunk : string) : void => {
        body += chunk;
    };

    var cbEnd = (chunk : string) : void => {
        if (typeof chunk !== "undefined") {
            body += chunk;
        };

        bodyJs = JSON.parse(body);
        console.log(JSON.stringify(bodyJs, null, 2));

        compileAll(bodyJs);
    };

    var cbError = (x, y, z) : void => {
        console.log("error", x, y, z);
    };

    console.log(response.statusCode);

    response.on("data", cbData);
    response.on("end", cbEnd);
    response.on("error", cbError);
};

http.request(options, callback).end();


/***********************************************************************
 * renderers
 */

compileAll = (metaApi : IMetaApi) : void => {
    var modules : IModuleDict = {};

    u.injectNickDict(metaApi.sheets);
    u.injectNickDict(metaApi.resources);

    for (var sheetName in metaApi.sheets) {
        if (metaApi.sheets.hasOwnProperty(sheetName)) {
            renderSheet(sheetName, metaApi.sheets[sheetName], modules, metaApi);
        }
    }

    for (var resourceName in metaApi.resources) {
        if (metaApi.resources.hasOwnProperty(resourceName)) {
            renderResource(resourceName, metaApi.resources[resourceName], modules, metaApi);
        }
    }

    var headerFooter = (relativeRoot : string, contents : string) : string => {
        var header = "";
        header += "/* tslint:disable:variable-name */\n\n";
        header += "import Base = require(\"" + canonicalizePath(relativeRoot + "../ResourcesBase") + "\");\n\n";

        var footer = "";
        footer += "/* tslint:enable:variable-name */\n";

        return header + contents + footer;
    };

    // generate sheet and resource modules
    (() => {
        for (var modulePath in modules) {
            if (modules.hasOwnProperty(modulePath)) {
                var absfp = "./Resources_/" + pyModuleToTsModule(modulePath) + ".ts";
                var relativeRoot = mkRelativeRoot(pyModuleToTsModule(modulePath));
                var contents = headerFooter(relativeRoot, modules[modulePath]);
                mkdirForFile(absfp);
                fs.writeFileSync(absfp, contents);
            }
        }
    })();

    // generate main module
    (() => {
        var rootModule = "";
        var relativeRoot = "./Resources_/";
        for (var modulePath in modules) {
            if (modules.hasOwnProperty(modulePath)) {
                rootModule += mkImportStatement(modulePath, relativeRoot, metaApi);
            }
        }
        rootModule += "\n";
        var absfp = "./Resources_.ts";
        fs.writeFileSync(absfp, headerFooter(relativeRoot, rootModule));
    })();
};

renderSheet = (modulePath : string, sheet : ISheet, modules : IModuleDict, metaApi : IMetaApi) : void => {
    var sheetI : string = "";
    var hasSheetI : string = "";

    sheetI += "export interface " + mkSheetName(sheet.nick) + " {\n";
    sheetI += mkFieldSignatures(sheet.fields, "    ", ";\n") + "\n";
    sheetI += "}\n\n";

    sheetI += "export interface Has" + mkSheetName(sheet.nick) + " {\n";
    sheetI += "    data : { \"" + modulePath + "\": " + mkSheetName(sheet.nick) + " }\n";
    sheetI += "}\n\n";

    hasSheetI += mkSheetSetter(sheet.nick, sheet.fields, "Has" + mkSheetName(sheet.nick));
    hasSheetI += mkSheetGetter(sheet.nick, "Has" + mkSheetName(sheet.nick));

    modules[modulePath] = sheetI + hasSheetI;
};

mkFieldSignatures = (fields : ISheetField[], tab : string, separator : string) : string =>
    u.mkThingList(
        fields,
        (field) => field.name + " : " + mkFieldType(field),
        tab, separator
    );

mkFieldAssignments = (fields : ISheetField[], tab : string) : string =>
    u.mkThingList(
        fields,
        (field) => field.name + ": " + field.name,
        tab, ",\n"
    );

enabledFields = (fields : ISheetField[], enableFlags ?: string) : ISheetField[] => {
    if (typeof enableFlags !== "string") {
        // if `flags` is not set, enable all fields
        return fields;
    } else {
        // if it is set, only enable those that have a least one flag
        // listed.  example: if a field has flags "ECM", and
        // `enabledFlags` is "CR", the field is enabled because it has
        // "C".
        var enabledFields = [];
        fields.map((field) => {
            if (mkFlags(field).match(new RegExp("[" + enableFlags + "]"))) {
                enabledFields.push(field);
            }
        });
        return enabledFields;
    }
};

mkSheetSetter = (nick : string, fields : ISheetField[], _selfType : string) : string => {
    var ef = enabledFields(fields, "ECM");

    if (!ef.length) {
        return "";
    } else {
        var os = [];
        os.push("export var _set" + mkSheetName(nick) + " = (");
        os.push("    _self : " + _selfType + ",");
        os.push(mkFieldSignatures(ef, "    ", ",\n"));
        os.push(") : " + _selfType + " => {");
        os.push("    _self.data[\"" + nick + "\"] = {");
        // set writeable fields to corresponding setter argument
        os.push(mkFieldAssignments(ef, "        ") + ",");
        // set hidden fields to null (or we will get type errors)
        (() => {
            var disabledFields = [];
            fields.map((field) => {
                if (ef.indexOf(field) === -1) {
                    disabledFields.push(field);
                }
            });
            os.push(u.mkThingList(disabledFields, (field) => field.name + ": null", "        ", ",\n"));
        })();
        os.push("    };");
        os.push("    return _self;");
        os.push("};\n");
        return u.intercalate(os, "\n");
    }
};

mkSheetGetter = (nick : string, _selfType : string) : string => {
    var os = [];
    os.push("export var _get" + mkSheetName(nick) + " = (");
    os.push("    _self : " + _selfType);
    os.push(") : " + mkSheetName(nick) + " => {");
    os.push("    return _self.data[\"" + nick + "\"];");
    os.push("};\n");
    return u.intercalate(os, "\n");
};

renderResource = (modulePath : string, resource : IResource, modules : IModuleDict, metaApi : IMetaApi) : void => {
    var resourceC : string = "";

    // imports
    var relativeRoot = mkRelativeRoot(pyModuleToTsModule(modulePath));
    for (var x in resource.sheets) {
        if (resource.sheets.hasOwnProperty(x)) {
            var name = resource.sheets[x];
            resourceC += mkImportStatement(name, relativeRoot, metaApi);
        }
    }
    resourceC += "\n";

    var mkConstructor = (tab : string) => {
        var os : string[] = [];

        if (resource.sheets.indexOf("adhocracy.sheets.name.IName") !== -1) {
            os.push("constructor();");
            os.push("constructor(name : string);");
            os.push("constructor() {");
            os.push("    super(\"" + modulePath + "\");");
            os.push("    var _self = this;");
            os.push("    if (name) {");
            os.push("        _self.setIName(name);");
            os.push("    }");
            os.push("}");
        } else {
            os.push("constructor() {");
            os.push("    super(\"" + modulePath + "\");");
            os.push("}");
        }

        return u.intercalate(os.map((s) => tab + s), "\n");
    };

    var mkDataDeclaration = (tab : string) : string => {
        var os : string[] = [];

        os.push("public data: {");
        for (var x in resource.sheets) {
            if (resource.sheets.hasOwnProperty(x)) {
                var name = resource.sheets[x];
                os.push("    \"" + name + "\" : " + mkModuleName(name, metaApi) + "." + mkSheetName(mkNick(name, metaApi)) + ";");
            }
        }
        os.push("};");

        return u.intercalate(os.map((s) => tab + s), "\n");
    };

    var mkGettersSetters = (tab : string) : string => {
        var os : string[] = [];

        // FIXME: this will be more interesting as soon as we get
        // around implementing read-only / optional / ... sheet
        // attributes.

        for (var x in resource.sheets) {
            if (resource.sheets.hasOwnProperty(x)) {
                var name = resource.sheets[x];
                os.push("public get" + mkSheetName(mkNick(name, metaApi)) + "() {");
                os.push("    return " + mkModuleName(name, metaApi) + "." + "_get" + mkSheetName(mkNick(name, metaApi)) + "(this);");
                os.push("}");

                var ef = enabledFields(metaApi.sheets[name].fields, "ECM");
                if (ef.length) {
                    os.push("public set" + mkSheetName(mkNick(name, metaApi)) + "(");
                    os.push(mkFieldSignatures(ef, "    ", ",\n"));
                    os.push(") {");
                    os.push("    var _self = this;\n");
                    os.push("    " + mkModuleName(name, metaApi) + "." + "_set" + mkSheetName(mkNick(name, metaApi)) + "(this,");
                    os.push(u.mkThingList(ef, (field) => field.name, "        ", ",\n    "));
                    os.push("    );");
                    os.push("    return _self;");
                    os.push("}");
                }
            }
        }
        return u.intercalate(os.map((s) => tab + s), "\n") + "";
    };

    resourceC += "class " + mkResourceClassName(mkNick(modulePath, metaApi)) + " extends Base.Resource {\n";
    resourceC += mkConstructor("    ") + "\n\n";
    resourceC += mkDataDeclaration("    ") + "\n\n";
    resourceC += mkGettersSetters("    ") + "\n";
    resourceC += "}\n\n";
    resourceC += "export = " + mkResourceClassName(mkNick(modulePath, metaApi)) + ";\n\n";

    modules[modulePath] = resourceC;
};

mkSheetName = (name : string) : string =>
    u.capitalizeHead(u.dotAndUnderscoreToCaml(name));

mkHasSheetName = (name : string) : string =>
    "HasSheet" + u.capitalizeHead(u.dotAndUnderscoreToCaml(name));

mkResourceClassName = (name : string) : string =>
    u.capitalizeHead(u.dotAndUnderscoreToCaml(name));

mkModuleName = (modulePath : string, metaApi : IMetaApi) : string => {
    if (metaApi.sheets.hasOwnProperty(modulePath)) {
        return "S" + u.capitalizeHead(u.dotAndUnderscoreToCaml(metaApi.sheets[modulePath].nick));
    } else if (metaApi.resources.hasOwnProperty(modulePath)) {
        return "R" + u.capitalizeHead(u.dotAndUnderscoreToCaml(metaApi.resources[modulePath].nick));
    } else {
        throw "mkNick: " + modulePath;
    }

};

mkImportStatement = (modulePath : string, relativeRoot : string, metaApi : IMetaApi) : string => {
    var tsModName = mkModuleName(modulePath, metaApi);
    var tsModPath = pyModuleToTsModule(modulePath);
    var tsModPathCanonicalized = canonicalizePath(relativeRoot + tsModPath);
    return "import " + tsModName + " = require(\"" + tsModPathCanonicalized + "\");\n";
};

mkNick = (modulePath : string, metaApi : IMetaApi) : string => {
    if (metaApi.sheets.hasOwnProperty(modulePath)) {
        return metaApi.sheets[modulePath].nick;
    } else if (metaApi.resources.hasOwnProperty(modulePath)) {
        return metaApi.resources[modulePath].nick;
    } else {
        throw "mkNick: " + modulePath;
    }
};

mkFieldType = (field : ISheetField) : string => {
    var result : string;

    switch (field.valuetype) {
    case "adhocracy.schema.AbsolutePath":
        result = "string";
        break;
    case "adhocracy.schema.Name":
        result = "string";
        break;
    case "adhocracy.schema.SingleLine":
        result = "string";
        break;
    case "adhocracy.schema.Text":
        result = "string";
        break;
    case "adhocracy.schema.Email":
        result = "string";
        break;
    case "adhocracy.schema.Password":
        result = "string";
        break;
    case "adhocracy.schema.DateTime":
        result = "string";
        break;
    case "adhocracy.schema.TimeZoneName":
        result = "string";
        break;
    default:
        throw "mkFieldType: unknown value " + field.valuetype;
    }

    if (field.hasOwnProperty("containertype")) {
        switch (field.containertype) {
        case "list":
            result += "[]";
            break;
        default:
            throw "mkFieldType: unknown container " + field.containertype;
        }
    }

    result += mkFlags(field, true);

    return result;
};

mkFlags = (field : ISheetField, comment ?: boolean) : string => {
    var flags : string = "";

    if (field.hasOwnProperty("readable") && field.readable) {
        flags += "R";
    }
    if (field.hasOwnProperty("editable") && field.editable) {
        flags += "E";
    }
    if (field.hasOwnProperty("creatable") && field.creatable) {
        flags += "C";
    }
    if (field.hasOwnProperty("create_mandatory") && field.create_mandatory) {
        flags += "M";
    }
    if (flags !== "" && comment) {
        flags = " /* " + flags + " */";
    }

    return flags;
};



/***********************************************************************
 * more general-purpose code
 */

mkdirForFile = (filepath : string) : void => {
    if (!_s.startsWith(filepath, "./") &&
        !_s.startsWith(filepath, "../")) {
        throw "mkdirForFile: path must start with './' or '../': " + filepath;
    }
    var dirpath : string[] = _s.words(filepath, "/");
    dirpath.pop();
    _fs.mkdirSync(u.intercalate(dirpath, "/"), 0755, true);
};

pyModuleToTsModule = (filepath : string) : string =>
    "./" + u.intercalate(_s.words(filepath, "\."), "/");

/**
 * The `relativeRoot` always points from file containing contents to
 * `.../Resources_/`.  The trailing `/` is important!
 */
mkRelativeRoot = (source : string) : string => {
    var arr = _s.words(source, "/");
    arr.pop();  // don't count leading `.`.
    arr.pop();  // just count directories, not the file name.
    return u.intercalate(arr.map(() => ".."), "/") + "/";
};

canonicalizePath = (filepath : string) : string => {
    return filepath
        .replace(/([^\.])\.\//g, "$1")
        .replace(/(\/)[^\/\.]+\/\.\.\//g, "$1");
};





// FIXME: before posting, delete read-only attributes / sheets from
// resources based on meta-api information.

// FIXME: _updSheet methods for all sheets, resources.

// FIXME: adapter code will be written manually written files in the
// directory tree under Resources_.  this means that we will commit
// auto-generated code, and also that we will have to think of a
// better solution for cleanup than `rm -r Resources`.  one option is
// to auto-generate a shell script during module generation that
// removes all generated files if executed.  (or, a bit less
// extravagant, just a file list that can be processed by a cleanup
// make or buildout rule or whatnot.)

// FIXME:
// mv Resources.Content to ResourcesBase.
// rm Resources.ts
// mv Resources_.ts to Resources.ts
// since Resources.ts is not required any more, add it to the Makefile explicitly
