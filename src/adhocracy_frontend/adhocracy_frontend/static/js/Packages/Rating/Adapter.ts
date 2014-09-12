import _ = require("lodash");

import ResourcesBase = require("../../ResourcesBase");
import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import RIRating = require("../../Resources_/adhocracy/resources/rating/IRating");
import RIRatingVersion = require("../../Resources_/adhocracy/resources/rating/IRatingVersion");
// import SICanRate = require("../../Resources_/adhocracy/sheets/rating/ICanRate");
// import SIRateable = require("../../Resources_/adhocracy/sheets/rating/IRateable");
import SIRating = require("../../Resources_/adhocracy/sheets/rating/IRating");
import SIVersionable = require("../../Resources_/adhocracy/sheets/versions/IVersionable");

import AdhRating = require("./Rating");


export class RatingAdapter implements AdhRating.IRatingAdapter<RIRatingVersion> {
    create(args : {
        preliminaryNames : PreliminaryNames;
        path ?: string;
        name ?: string;
        subject : string;
        target : string;
        follows : string;
    }) : RIRatingVersion {
        var resource = new RIRatingVersion({
            preliminaryNames: args.preliminaryNames,
            path: args.path,
            name: args.name
        });
        resource.data["adhocracy.sheets.rating.IRating"] =
            new SIRating.AdhocracySheetsRatingIRating({subject: args.subject, target: args.target});

        resource.data["adhocracy.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracySheetsVersionsIVersionable({follows: [args.follows]});

        return resource;
    }

    createItem(args : { preliminaryNames : PreliminaryNames; path ?: string }) : RIRating {
        return new RIRating(args);
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

    content(resource : RIRatingVersion) : string;
    content(resource : RIRatingVersion, value : string) : RIRatingVersion;
    content(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rating.IRating"].content = value;
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rating.IRating"].content;
        }
    }

    refersTo(resource : RIRatingVersion) : string;
    refersTo(resource : RIRatingVersion, value : string) : RIRatingVersion;
    refersTo(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy.sheets.rating.IRating"].target = value;
            return resource;
        } else {
            return resource.data["adhocracy.sheets.rating.IRating"].target;
        }
    }

    creator(resource : RIRatingVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].creator;
    }

    creationDate(resource : RIRatingVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].item_creation_date;
    }

    modificationDate(resource : RIRatingVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].modification_date;
    }
}
