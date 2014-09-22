import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");
import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import RIRate = require("../../Resources_/adhocracy/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy/resources/rate/IRateVersion");
// import SICanRate = require("../../Resources_/adhocracy/sheets/rate/ICanRate");
// import SIRateable = require("../../Resources_/adhocracy/sheets/rate/IRateable");
import SIRate = require("../../Resources_/adhocracy/sheets/rate/IRate");
import SIVersionable = require("../../Resources_/adhocracy/sheets/versions/IVersionable");

import AdhRate = require("./Rate");


export class RateAdapter implements AdhRate.IRateAdapter<RIRateVersion> {
    create(args : {
        preliminaryNames : PreliminaryNames;
        path ?: string;
        name ?: string;
        subject : string;
        object : string;
        rate ?: number;
        follows : string;
    }) : RIRateVersion {
        var resource = new RIRateVersion({
            preliminaryNames: args.preliminaryNames,
            path: args.path,
            name: args.name
        });
        if (typeof args.rate === "undefined") {
            args.rate = 0;
        }

        resource.data["adhocracy.sheets.rate.IRate"] =
            new SIRate.AdhocracySheetsRateIRate({subject: args.subject, object: args.object, rate: args.rate });

        resource.data["adhocracy.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracySheetsVersionsIVersionable({follows: [args.follows]});

        return resource;
    }

    createItem(args : { preliminaryNames : PreliminaryNames; path ?: string }) : RIRate {
        return new RIRate(args);
    }

    // FIXME: move to a service (also do it in Comment)
    derive<R extends ResourcesBase.Resource>(oldVersion : R, settings) : R {
        var resource = new (<any>oldVersion).constructor(settings);

        _.forOwn(oldVersion.data, (sheet, key) => {
            resource.data[key] = new sheet.constructor(settings);

            _.forOwn(sheet, (value, field) => {
                resource.data[key][field] = _.cloneDeep(value);
            });
        });

        resource.data["adhocracy.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracySheetsVersionsIVersionable({follows: [oldVersion.path]});

        return resource;
    }

    is(resource : ResourcesBase.Resource) : boolean {
        return resource.content_type === "adhocracy.resources.rate.IRate";
    }

    subject(resource : RIRateVersion) : string;
    subject(resource : RIRateVersion, value : string) : RIRateVersion;
    subject(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rate.IRate"].subject = value;
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rate.IRate"].subject;
        }
    }

    object(resource : RIRateVersion) : string;
    object(resource : RIRateVersion, value : string) : RIRateVersion;
    object(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rate.IRate"].object = value;
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rate.IRate"].object;
        }
    }

    rate(resource : RIRateVersion) : AdhRate.RateValue;
    rate(resource : RIRateVersion, value : AdhRate.RateValue) : RIRateVersion;
    rate(resource, value?) {
        var sheet : { rate: number } = resource.data["adhocracy.sheets.rate.IRate"];
        if (typeof value !== "undefined") {
            sheet.rate = value;
            return resource;
        } else {
            return sheet.rate;
        }
    }

    creator(resource : RIRateVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].creator;
    }

    creationDate(resource : RIRateVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].item_creation_date;
    }

    modificationDate(resource : RIRateVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].modification_date;
    }
}
