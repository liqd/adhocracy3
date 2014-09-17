import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");
import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import RIRate = require("../../Resources_/adhocracy/resources/rate/IRate");
import RIRateVersion = require("../../Resources_/adhocracy/resources/rate/IRateVersion");
// import SICanRate = require("../../Resources_/adhocracy/sheets/rate/ICanRate");
// import SIRateable = require("../../Resources_/adhocracy/sheets/rate/IRateable");
import SIRate = require("../../Resources_/adhocracy/sheets/rate/IRate");
import SIVersionable = require("../../Resources_/adhocracy/sheets/versions/IVersionable");

import AdhRating = require("./Rating");


export class RatingAdapter implements AdhRating.IRatingAdapter<RIRateVersion> {
    create(args : {
        preliminaryNames : PreliminaryNames;
        path ?: string;
        name ?: string;
        subject : string;
        target : string;
        follows : string;
    }) : RIRateVersion {
        var resource = new RIRateVersion({
            preliminaryNames: args.preliminaryNames,
            path: args.path,
            name: args.name
        });
        resource.data["adhocracy.sheets.rate.IRate"] =
            new SIRate.AdhocracySheetsRateIRate({subject: args.subject, object: args.target, rate: 0});

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

    target(resource : RIRateVersion) : string;
    target(resource : RIRateVersion, value : string) : RIRateVersion;
    target(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rating.IRating"].target = value;
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rating.IRating"].target;
        }
    }

    value(resource : RIRateVersion) : AdhRating.RatingValue;
    value(resource : RIRateVersion, value : AdhRating.RatingValue) : RIRateVersion;
    value(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rating.IRating"].value = AdhRating.RatingValue[value];
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rating.IRating"].value;
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
